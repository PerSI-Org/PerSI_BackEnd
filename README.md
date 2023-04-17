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

## API 목록

### 화자 등록

#### Request

- URI: `/speakers`
- Method: `POST`
- Headers:
    - `Content-Type`: `application/json`
- Body:

    ```json
    {
        "name": "김나현",
        "profile_img": "image2"
    }
    ```

#### Response

- Status: `200 OK`
- Body:

    ```json
    {
        "data": [
            {
                "name": "김나현",
                "profile_img": "image2"
            }
        ],
        "code": 200,
        "message": "Speaker created successfully."
    }
    ```

### 화자 목록 조회

#### Request

- URI: `/speakers`
- Method: `GET`

#### Response

- Status: `200 OK`
- Body:

    ```json
    {
        "data": [
            {
                "name": "김나현",
                "profile_img": "image2"
            },
            {
                "name": "이민성",
                "profile_img": "image3"
            }
        ],
        "code": 200,
        "message": "Speakers retrieved successfully."
    }
    ```

                   
