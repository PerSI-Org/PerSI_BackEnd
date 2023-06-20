# PerSI_BackEnd

PerSI_BackEnd는 청각장애인을 위한 어플리케이션 PerSI의 백엔드 서버입니다.

## 개발 환경

- Python 3.8.5
- FastAPI 0.68.1
- MongoDB 5.0.3

## 프로젝트 실행 방법

### 1. MongoDB 설치

[몽고디비 공식 홈페이지](https://www.mongodb.com/)에서 MongoDB를 다운로드 받아 설치합니다.

### 2. 가상 환경 설정

$ python3 -m venv venv
$ source venv/bin/activate

### 3. 의존성 패키지 설치

$ pip install -r requirements.txt

### 4. MongoDB 실행

$ mongod --dbpath [데이터베이스 경로]

### 5. 서버 실행

$ python ./main.py

### 6. API 목록

$ http://localhost:8000/docs#/

### 추가 환경 설정

- PerSI_BackEnd/server/ 디렉토리 아래에 Wav2Vec, pyannote 레포지토리를 클론하여 넣어주세요.
- 두 레포지토리는 server 브랜치를 기준으로 클론 해주세요.



                   
