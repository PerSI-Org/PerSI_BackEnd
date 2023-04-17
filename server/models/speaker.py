from pydantic import BaseModel
from odmantic import Model
from typing import Optional


class Speaker(Model):
    name: str
    profile_img: str


class UpdateSpeakerModel(Model):
    name: Optional[str]
    profile_img: Optional[str]

    class Config:
        schema_extra = {
            "example": {
                "name": "김나현",
                "profile_img": "image2"
            }
        }


def ResponseModel(data, message):
    return {
        "data": [data],
        "code": 200,
        "message": message
    }


def ErrorResponseModel(error, code, message):
    return {"error": error, "code": code, "message": message}
