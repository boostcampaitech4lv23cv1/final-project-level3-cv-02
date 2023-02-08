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

# **🎹개요**
<br></br>

<div align=center>
<img src="https://i.ibb.co/Lthw9hq/Untitled.png">
<br></br>

<h4>악보를 가지고 있으나 연주가 어렵다고 느낄 때 음악으로 변환해주는 서비스를 제공합니다.</h4>
</div>
<br></br>


# **💻Service architecture**
<div align=center>
<img src="https://i.ibb.co/H2gfYtZ/2023-02-08-150121.png" height=70% width=70%>
</div>

<br></br>

# **📦Data**
## **Deepscore V2**
https://tuggeluk.github.io/deepscores/
<div align=center>
<img src="https://i.ibb.co/bRrkP1T/Untitled-4.png">
</div>

```
# Example code
.
|-- deepscores_test.json
|-- deepscores_train.json
|-- images
|   |-- image1.png
|   |-- image2.png
|   `-- ...
|-- instance
|   |-- image1.png
|   |-- image2.png
|   `-- ...
|-- segmentation
|   |-- image1.png
|   |-- image2.png
|   `-- ...
|-- deepscores_test.json
`-- deepscores_train.json
```

<br></br>

# **🔑Modeling**
<div align=center>
<img src="https://i.ibb.co/vkDJhww/Untitled-1.png">
</div>

## **1. Model**
### **Yolo v7**
https://github.com/WongKinYiu/yolov7

## **2. Pre-processing**
> dataset을 그대로 학습시킬 경우 불필요한 정보가 많아 전처리 과정이 필요했습니다.
<div align=center>
<img src="https://i.ibb.co/y4MbcVB/2023-02-08-155421.png" height=70% width=70%>
</div>

악상기호와 음표만 남기기 위해 오선지의 위치 정보만 저장한 후 삭제합니다.
이후 악보를 이진화하여 필요한 정보만 추출한 후 학습시킵니다.

## **3. Post-processing**
> model의 prediction을 기반으로 연주할 때 필요한 정보를 계산합니다.

<div align=center>
<img src="https://i.ibb.co/XtzXBp7/2023-02-08-155311.png" height=70% width=70%>
</div>

- conversion from yolo: 정규화된 bbox 좌표를 일반 악보 좌표로 변환합니다.
- merge bbox: 한 음표나 기호를 여러번 예측했다면 하나로 합칩니다.
- noise removal: 예측 결과의 noise를 제거합니다.
- beat detection: 음표의 박자 정보를 계산합니다.
- measure calculation: 음표가 몇번째 마디에 속해있는지 계산합니다.
- pitch detection: 계이름을 반환합니다.
- SFN(Sharp Flat Natural) detection: 조표를 적용합니다.

## **4. Conversion to MusicXML**
> post processing 결과를 MusicXML 형식으로 변환합니다.
<div align=center>
<img src="https://i.ibb.co/HD0bBVT/2023-02-08-155532.png" height=70% width=70%>
</div>

<br></br>


# **📁Folder Structure**

```
app/
.
|-- constant.py
|-- db
|   |-- __init__.py
|   |-- connection.py
|   |-- core
|   |   |-- __init__.py
|   |   |-- config.py
|   |   |-- db_login.py
|   |   `-- key.json
|   |-- crud
|   |   |-- __init__.py
|   |   |-- image_bundle.py
|   |   |-- sound.py
|   |   `-- users.py
|   |-- models
|   |   |-- __init__.py
|   |   |-- image.py
|   |   |-- image_bundle.py
|   |   |-- sound.py
|   |   `-- users.py
|   |-- routes
|   |   |-- __init__.py
|   |   |-- image_bundle.py
|   |   |-- sound.py
|   |   `-- users.py
|   |-- schemas
|   |   |-- __init__.py
|   |   |-- image.py
|   |   |-- image_bundle.py
|   |   |-- sound.py
|   |   `-- users.py
|   |-- service
|   |   |-- __init__.py
|   |   |-- image_bundle.py
|   |   |-- sound.py
|   |   `-- users.py
|   `-- session.py
|-- main.py
|-- output
|-- poetry.lock
|-- pyproject.toml
|-- secret.py
|-- service.py
|-- static
|   |-- css
|   |   |-- css files
|       `-- ******.css
|   |-- fonts
|       `-- font files
|   `-- js
|   |   |-- js files
|       `-- ******.js
|-- templates
|   |-- html files
|   `-- ******.html
`-- utils.py

MusicXML2Audio/
.
|-- constant.py
|-- converter
|   |-- MXL2midi.py
|   |-- midi2wav.py
|   `-- wav2sound.py
|-- data
|-- install_packages.sh
|-- main.py
`-- midi2audio.py
```
<br></br>


# 📄Reference
- DeepScores -- A Dataset for Segmentation, Detection and Classification of Tiny Objects https://arxiv.org/pdf/1804.00525.pdf
- Understanding Optical Music Recognition https://arxiv.org/abs/1908.03608
- https://github.com/yvan674/obb_anns
- https://github.com/BreezeWhite/oemer/tree/main/oemer
- https://github.com/FluidSynth/fluidsynth
- https://github.com/bzamecnik/midi2audio


<div align=center>  

![Footer](https://capsule-render.vercel.app/api?type=waving&color=7F7FD5&fontColor=FFFFFF&height=200&section=footer)
