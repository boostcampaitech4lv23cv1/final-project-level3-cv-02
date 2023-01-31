import cv2
import numpy as np

def threshold(image_path):
    image = cv2.imread(image_path)
    if 'png' in image_path: 
        image = cv2.cvtColor(image, cv2.COLOR_BGRA2GRAY)
    elif 'jpg' in image_path: 
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    ret, image = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
    return image

def remove_noise(image_path): 
    image = threshold(image_path) 
    mask = np.zeros(image.shape, np.uint8)  # 보표 영역만 추출하기 위해 마스크 생성

    cnt, labels, stats, centroids = cv2.connectedComponentsWithStats(image)  # 레이블링
    for i in range(1, cnt):
        x, y, w, h, area = stats[i]
        if w > image.shape[1] * 0.3:  # 보표 영역에만
            cv2.rectangle(mask, (x, y, w, h), (255, 0, 0), -1)  # 사각형 그리기

    masked_image = cv2.bitwise_and(image, mask) 

    return masked_image



def remove_staves(image):
    height, width = image.shape
    staves = []  # 오선의 좌표들이 저장될 리스트

    for row in range(height):
        pixels = 0
        for col in range(width):
            pixels += (image[row][col] == 255)  # 한 행에 존재하는 흰색 픽셀의 개수를 셈
        if pixels >= width * 0.5:  # 이미지 넓이의 50% 이상이라면
            if len(staves) == 0 or abs(staves[-1][0] + staves[-1][1] - row) > 1:  # 첫 오선이거나 이전에 검출된 오선과 다른 오선
                staves.append([row, 0])  # 오선 추가 [오선의 y 좌표][오선 높이]
            else:  # 이전에 검출된 오선과 같은 오선
                staves[-1][1] += 1  # 높이 업데이트

    for staff in range(len(staves)):
        top_pixel = staves[staff][0]  # 오선의 최상단 y 좌표
        bot_pixel = staves[staff][0] + staves[staff][1]  # 오선의 최하단 y 좌표 (오선의 최상단 y 좌표 + 오선 높이)
        for col in range(width):
            if image[top_pixel - 1][col] == 0 and image[bot_pixel + 1][col] == 0:  # 오선 위, 아래로 픽셀이 있는지 탐색
                for row in range(top_pixel, bot_pixel + 1):
                    image[row][col] = 0  # 오선을 지움

    return image, [x[0] for x in staves]



def normalization(image, staves, standard):
    avg_distance = 0
    lines = int(len(staves) / 5)  # 보표의 개수
    for line in range(lines):
        for staff in range(4):
            staff_above = staves[line * 5 + staff]
            staff_below = staves[line * 5 + staff + 1]
            avg_distance += abs(staff_above - staff_below)  # 오선의 간격을 누적해서 더해줌
    avg_distance /= len(staves) - lines  # 오선 간의 평균 간격

    height, width = image.shape  # 이미지의 높이와 넓이
    weight = standard / avg_distance  # 기준으로 정한 오선 간격을 이용해 가중치를 구함
    new_width = int(width * weight)  # 이미지의 넓이에 가중치를 곱해줌
    new_height = int(height * weight)  # 이미지의 높이에 가중치를 곱해줌

    # image = cv2.resize(image, (new_width, new_height))  # 이미지 리사이징
    ret, image = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)  # 이미지 이진화
    # staves = [x * weight for x in staves]  # 오선 좌표에도 가중치를 곱해줌
    
    f = open('/opt/ml/yolov7/staves.txt', 'w')
    for i in range(len(staves)): 
        f.write('{}\n'.format(staves[i]))
    f.close() 

    return image


"""
def weighted(value):
    standard = 10
    return int(value * (standard / 10))

def closing(image):
    kernel = np.ones((weighted(5), weighted(5)), np.uint8)
    image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
    return image

def get_center(y, h):
    return (y + y + h) / 2

def put_text(image, text, loc):
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(image, str(text), loc, font, 0.6, (255, 0, 0), 2)

def object_detection(image, staves):
    lines = int(len(staves) / 5)  # 보표의 개수
    objects = []  # 구성요소 정보가 저장될 리스트

    closing_image = closing(image)
    cnt, labels, stats, centroids = cv2.connectedComponentsWithStats(closing_image)  # 모든 객체 검출하기
    for i in range(1, cnt):
        (x, y, w, h, area) = stats[i]
        # cv2.rectangle(image, (x, y, w, h), (255, 0, 0), 1)
        objects.append([x,y,w,h,area])
        # if w >= weighted(5) and h >= weighted(5):  # 악보의 구성요소가 되기 위한 넓이, 높이 조건
        #     center = get_center(y, h)
        #     for line in range(lines):
        #         area_top = staves[line * 5] - weighted(20)  # 위치 조건 (상단)
        #         area_bot = staves[(line + 1) * 5 - 1] + weighted(20)  # 위치 조건 (하단)
        #         if area_top <= center <= area_bot:
        #             objects.append([line, (x, y, w, h, area)])  # 객체 리스트에 보표 번호와 객체의 정보(위치, 크기)를 추가

    objects.sort()  # 보표 번호 → x 좌표 순으로 오름차순 정렬

    return image, objects



VERTICAL = True
HORIZONTAL = False

def get_line(image, axis, axis_value, start, end, length):
    if axis:
        points = [(i, axis_value) for i in range(start, end)]  # 수직 탐색
    else:
        points = [(axis_value, i) for i in range(start, end)]  # 수평 탐색
    pixels = 0
    for i in range(len(points)):
        (y, x) = points[i]
        pixels += (image[y][x] == 255)  # 흰색 픽셀의 개수를 셈
        next_point = image[y + 1][x] if axis else image[y][x + 1]  # 다음 탐색할 지점
        if next_point == 0 or i == len(points) - 1:  # 선이 끊기거나 마지막 탐색임
            if pixels >= weighted(length):
                break  # 찾는 길이의 직선을 찾았으므로 탐색을 중지함
            else:
                pixels = 0  # 찾는 길이에 도달하기 전에 선이 끊김 (남은 범위 다시 탐색)
    return y if axis else x, pixels

def stem_detection(image, stats, length):
    (x, y, w, h, area) = stats
    stems = []  # 기둥 정보 (x, y, w, h)
    for col in range(x, x + w):
        end, pixels = get_line(image, VERTICAL, col, y, y + h, length)
        if pixels:
            if len(stems) == 0 or abs(stems[-1][0] + stems[-1][2] - col) >= 1:
                (x, y, w, h) = col, end - pixels + 1, 1, pixels
                stems.append([x, y, w, h])
            else:
                stems[-1][2] += 1
    return stems

def object_analysis(image, objects):
    for obj in objects:
        stats = obj[1]
        stems = stem_detection(image, stats, 30)  # 객체 내의 모든 직선들을 검출함
        direction = None
        if len(stems) > 0:  # 직선이 1개 이상 존재함
            if stems[0][0] - stats[0] >= weighted(5):  # 직선이 나중에 발견되면
                direction = True  # 정 방향 음표
            else:  # 직선이 일찍 발견되면
                direction = False  # 역 방향 음표
        obj.append(stems)  # 객체 리스트에 직선 리스트를 추가
        obj.append(direction)  # 객체 리스트에 음표 방향을 추가

    return image, objects



def recognition(image, staves, objects):
    key = 0
    time_signature = False
    beats = []  # 박자 리스트
    pitches = []  # 음이름 리스트

    for i in range(1, len(objects)):
        obj = objects[i]
        line = obj[0]
        stats = obj[1]
        stems = obj[2]
        direction = obj[3]
        (x, y, w, h, area) = stats
        staff = staves[line * 5: (line + 1) * 5]
        if not time_signature:  # 조표가 완전히 탐색되지 않음 (아직 박자표를 찾지 못함)
            ts, temp_key = recognize_key(image, staff, stats)
            time_signature = ts
            key += temp_key
        else:  # 조표가 완전히 탐색되었음
            pass

        cv2.rectangle(image, (x, y, w, h), (255, 0, 0), 1)
        put_text(image, i, (x, y - weighted(30)))

    return image, key, beats, pitches

def recognize_key(image, staves, stats):
    (x, y, w, h, area) = stats
    ts_conditions = (
        staves[0] + weighted(5) >= y >= staves[0] - weighted(5) and  # 상단 위치 조건
        staves[4] + weighted(5) >= y + h >= staves[4] - weighted(5) and  # 하단 위치 조건
        staves[2] + weighted(5) >= get_center(y, h) >= staves[2] - weighted(5) and  # 중단 위치 조건
        weighted(18) >= w >= weighted(10) and  # 넓이 조건
        weighted(45) >= h >= weighted(35)  # 높이 조건
    )
    if ts_conditions:
            return True, 0
    else:  # 조표가 있을 경우 (다장조를 제외한 모든 조)
        stems = stem_detection(image, stats, 20)
        if stems[0][0] - x >= weighted(3):  # 직선이 나중에 발견되면
            key = int(10 * len(stems) / 2)  # 샾
        else:  # 직선이 일찍 발견되면
            key = 100 * len(stems)  # 플랫

    return False, key

def recognition(image, staves, objects):
    key = 0
    time_signature = False
    beats = []  # 박자 리스트
    pitches = []  # 음이름 리스트

    for i in range(1, len(objects)):
        obj = objects[i]
        line = obj[0]
        stats = obj[1]
        stems = obj[2]
        direction = obj[3]
        (x, y, w, h, area) = stats
        staff = staves[line * 5: (line + 1) * 5]
        if not time_signature:  # 조표가 완전히 탐색되지 않음 (아직 박자표를 찾지 못함)
            ts, temp_key = recognize_key(image, staff, stats)
            time_signature = ts
            key += temp_key
            if time_signature:
                put_text(image, key, (x, y + h + weighted(20)))
        else:  # 조표가 완전히 탐색되었음
            pass

        cv2.rectangle(image, (x, y, w, h), (255, 0, 0), 1)
        put_text(image, i, (x, y - weighted(30)))

    return image, key, beats, pitches




def count_rect_pixels(image, rect):
    x, y, w, h = rect
    pixels = 0
    for row in range(y, y + h):
        for col in range(x, x + w):
            if image[row][col] == 255:
                pixels += 1
    return pixels

def recognize_note_head(image, stem, direction):
    (x, y, w, h) = stem
    if direction:  # 정 방향 음표
        area_top = y + h - weighted(7)  # 음표 머리를 탐색할 위치 (상단)
        area_bot = y + h + weighted(7)  # 음표 머리를 탐색할 위치 (하단)
        area_left = x - weighted(14)  # 음표 머리를 탐색할 위치 (좌측)
        area_right = x  # 음표 머리를 탐색할 위치 (우측)
    else:  # 역 방향 음표
        area_top = y - weighted(7)  # 음표 머리를 탐색할 위치 (상단)
        area_bot = y + weighted(7)  # 음표 머리를 탐색할 위치 (하단)
        area_left = x + w  # 음표 머리를 탐색할 위치 (좌측)
        area_right = x + w + weighted(14)  # 음표 머리를 탐색할 위치 (우측)

    # cv2.rectangle(image, (area_left, area_top, area_right - area_left, area_bot - area_top), (255, 0, 0), 1)

    cnt = 0  # cnt = 끊기지 않고 이어져 있는 선의 개수를 셈
    cnt_max = 0  # cnt_max = cnt 중 가장 큰 값
    head_center = 0
    pixel_cnt = count_rect_pixels(image, (area_left, area_top, area_right - area_left, area_bot - area_top))

    for row in range(area_top, area_bot):
        end, pixels = get_line(image, HORIZONTAL, row, area_left, area_right, 5)
        pixels += 1
        if pixels:
            cnt += 1
            cnt_max = max(cnt_max, pixels)
            head_center += row

    head_exist = (cnt >= 3 and pixel_cnt >= 50)
    head_fill = (cnt >= 8 and cnt_max >= 9 and pixel_cnt >= 80)
    head_center /= cnt

    pass

def recognize_note_tail(image, index, stem, direction):
    (x, y, w, h) = stem
    if direction:  # 정 방향 음표
        area_top = y  # 음표 꼬리를 탐색할 위치 (상단)
        area_bot = y + h - weighted(10)  # 음표 꼬리를 탐색할 위치 (하단)
        area_left = x + w  # 음표 꼬리를 탐색할 위치 (좌측)
        area_right = x + w + weighted(10)  # 음표 꼬리를 탐색할 위치 (우측)
    else:  # 역 방향 음표
        area_top = y + weighted(10)  # 음표 꼬리를 탐색할 위치 (상단)
        area_bot = y + h  # 음표 꼬리를 탐색할 위치 (하단)
        area_left = x + w  # 음표 꼬리를 탐색할 위치 (좌측)
        area_right = x + w + weighted(10)  # 음표 꼬리를 탐색할 위치 (우측)
    if index:
        area_col = x - weighted(3)  # 음표 꼬리를 탐색할 위치 (열)
    else:
        area_col = x + w + weighted(3)  # 음표 꼬리를 탐색할 위치 (열)

    cnt = 0

    flag = False
    for row in range(area_top, area_bot):
        if not flag and image[row][area_col] == 255:
            flag = True
            cnt += 1
        elif flag and image[row][area_col] == 0:
            flag = False

    put_text(image, cnt, (x - weighted(10), y + h + weighted(20)))

    pass

def recognize_note(image, staff, stats, stems, direction):
    (x, y, w, h, area) = stats
    notes = []
    pitches = []
    note_condition = (
        len(stems) and
        w >= weighted(10) and  # 넓이 조건
        h >= weighted(35) and  # 높이 조건
        area >= weighted(95)  # 픽셀 갯수 조건
    )
    if note_condition:
        for i in range(len(stems)):
            stem = stems[i]
            head_exist, head_fill, head_center = recognize_note_head(image, stem, direction)
            if head_exist:
                recognize_note_tail(image, i, stem, direction)

    pass

def recognition(image, staves, objects):
    key = 0
    time_signature = False
    beats = []  # 박자 리스트
    pitches = []  # 음이름 리스트

    for i in range(1, len(objects)):
        obj = objects[i]
        line = obj[0]
        stats = obj[1]
        stems = obj[2]
        direction = obj[3]
        (x, y, w, h, area) = stats
        staff = staves[line * 5: (line + 1) * 5]
        if not time_signature:  # 조표가 완전히 탐색되지 않음 (아직 박자표를 찾지 못함)
            ts, temp_key = recognize_key(image, staff, stats)
            time_signature = ts
            key += temp_key
        else:  # 조표가 완전히 탐색되었음
            recognize_note(image, staff, stats, stems, direction)

        cv2.rectangle(image, (x, y, w, h), (255, 0, 0), 1)
        put_text(image, i, (x, y - weighted(20)))

    return image, key, beats, pitches
"""