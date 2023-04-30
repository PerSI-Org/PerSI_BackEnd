from odmantic import Model, ObjectId
from typing import Optional
from pydantic import BaseModel, Field


class Speaker(Model):
    name: str
    voice_sample: str
    user_id: ObjectId


class SpeakerUpdate(BaseModel):
    name: Optional[str] = Field(None, example="김지우")
    voice_sample: Optional[str] = Field(None, example="file/path/sample.mp3")
