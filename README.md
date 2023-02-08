<div align=center>

![header](https://capsule-render.vercel.app/api?type=waving&text=Mastro%20-%20악보를%20음악으로&color=7F7FD5&fontColor=FFFFFF&fontSize=50&height=200)

</div> 

# **💘비전로켓단**

<div align=center>
<br></br>

|<img src="https://user-images.githubusercontent.com/72690566/200118081-7f8e4279-04ef-4269-abde-80b9ea89e87a.png" width="80">|<img src="https://user-images.githubusercontent.com/72690566/200118119-d21769d2-ff0d-4e15-9e6d-aa863e700f36.png" width="80">|<img src="https://user-images.githubusercontent.com/72690566/200118141-2de150f1-98cb-4cbd-8ce8-419c1ebb0678.png" width="80">|<img src="https://user-images.githubusercontent.com/72690566/200118162-f25ae93e-18c1-462f-8298-c6ff5c95ee79.png" width="80">|<img src="https://user-images.githubusercontent.com/72690566/200118175-ba5859db-5a2f-4457-a8e2-878f8cc1140e.png" width="80">|
|:---:|:---:|:---:|:---:|:---:|
|구상모|배서현|이영진|권규보|오한별|
|T4008|T4095|T4155|T4011|T4128|

</div>
<br></br>

# **👫팀 구성 및 역할**

<div align=center>

|전체|서비스 시나리오 정의 및 구체화|
|:----------:|:------:|
|구상모|oemer custom, Web Back-end(사용자 인증)|
|권규보|Model pipeline, Model training, convert to XML|
|배서현|dataset research, Web Front-end|
|오한별|model pre-processing, model post-processing​|
|이영진|Web Back-end(DB, server)|

</div>
<br></br>


# **⭐Demo**

<div align=center>

[![Video Label](http://img.youtube.com/vi/F0P3p_2fejc/0.jpg)](https://youtu.be/F0P3p_2fejc)

</div>

<br></br>

# **📥Start**
```
# clone repo
git clone https://github.com/boostcampaitech4lv23cv1/level3_productserving-level3-cv-02.git

# install requirements
pip install -r requirements.txt

# install to convert mp3 package
cd MusicXML2Audio/
sh install_packages.sh

# Run
cd ../app/
python main.py
```
<br></br>

# **📁Folder Structure**
```
(TODO: 추가)
```

<br></br>

# **🎹개요**

<div align=center>
<img src="https://i.ibb.co/Lthw9hq/Untitled.png">
<img src="https://i.ibb.co/xqjtpb5/Untitled-2.png">
</div>

<br></br>

# **🔑 Modeling**

<img src="https://i.ibb.co/vkDJhww/Untitled-1.png">

## **1. Data**
- dataset이야기

## **2. Model**
### 1. Model
Yolo v7

### 2. Pre-processing

<div align=center>
<img src="https://i.ibb.co/y4MbcVB/2023-02-08-155421.png" height=70% width=70%>
</div>

- 오선지 삭제
- 이진화

### **3. Post-processing**

<div align=center>
<img src="https://i.ibb.co/XtzXBp7/2023-02-08-155311.png" height=70% width=70%>
</div>

- conversion from yolo: yolo가 내보낸 음표와 symbol들의 정규화된 bbox 좌표를 일반 악보 좌표로 변환
- merge bbox: yolo가 한 음표나 symbol을 여러번 pred해서 겹치는 bbox들을 한 bbox로 합침 
- noise removal: 음표 pred에서 음표가 아닌 것을 pred한 경우 지움 / symbol pred에서 symbol이 아닌 것을 pred한 경우 지움 
- beat detection: note head의 label과 flag, augmentation dot의 정보를 종합하여 해당 음표의 박자 정보를 반환 
- measure calculation: 음표들의 박자 정보와 쉼표 정보를 종합하여 음표들이 어느 마디에 속하는지 계산
- pitch detection: 오선지의 위치와 note head의 위치를 종합하여 계이름을 반환 
- SFN(Sharp Flat Natural) detection: SFN이 있는지 확인하고 있으면 해당하는 음표에 적용

## **3. Conversion to MusicXML**
<div align=center>
<img src="https://i.ibb.co/HD0bBVT/2023-02-08-155532.png" height=70% width=70%>
</div>
<br></br>

# **💻Serving**

## **1. Service Architecture**

<div align=center>
<img src="https://i.ibb.co/H2gfYtZ/2023-02-08-150121.png" height=70% width=70%>

</div>
<br></br>

## **2. User Scenario**

<div align=center>
<img src="https://i.ibb.co/94P87T0/2023-02-08-150922.png">

</div>
<br></br>


# 📄참고
- DeepScores -- A Dataset for Segmentation, Detection and Classification of Tiny Objects https://arxiv.org/pdf/1804.00525.pdf
- Understanding Optical Music Recognition https://arxiv.org/abs/1908.03608

- DeepscoreV2 https://zenodo.org/record/4012193#.Y8C5rnZBxmN

- https://github.com/yvan674/obb_anns
- https://github.com/BreezeWhite/oemer/tree/main/oemer
- https://github.com/FluidSynth/fluidsynth
- https://github.com/bzamecnik/midi2audio


<div align=center>  

![Footer](https://capsule-render.vercel.app/api?type=waving&color=7F7FD5&fontColor=FFFFFF&height=200&section=footer)