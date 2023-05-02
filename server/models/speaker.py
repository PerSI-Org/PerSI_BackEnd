from odmantic import Model, ObjectId
from typing import Optional
from pydantic import BaseModel, Field


class Speaker(Model):
    name: str
    voice_sample: str
    user_id: ObjectId


class SpeakerCreate(BaseModel):
    name: str = Field(None, example="김지우")
    voice_sample: str = Field(None, example="file/path/sample.mp3")
    user_id: str


class SpeakerUpdate(BaseModel):
    name: Optional[str] = Field(None, example="김지우")
    voice_sample: Optional[str] = Field(None, example="file/path/sample.mp3")
