from odmantic import Model, ObjectId
from typing import Optional, List
from pydantic import BaseModel, Field


class Speaker(Model):
    name: str
    voice_sample: Optional[str]
    call_samples: Optional[List[str]]
    profile_image: Optional[str]
    register_number: Optional[int]
    user_id: ObjectId


class SpeakerCreate(BaseModel):
    name: str = Field(None, example="김지우")
    voice_sample: Optional[str] = Field(None, example="https://storage.googleapis.com/persi-server/test_file.wav")
    call_samples: Optional[List[str]] = Field(
        None, example=["https://storage.googleapis.com/persi-server/test_file.wav"])
    profile_image: Optional[str] = Field(None, example="https://storage.googleapis.com/persi-server/test_file.jpg")
    user_id: str


class SpeakerUpdate(BaseModel):
    name: Optional[str] = Field(None, example="김지우")
    voice_sample: Optional[str] = Field(None, example="https://storage.googleapis.com/persi-server/test_file.wav")
    call_samples: Optional[List[str]] = Field(
        None, example=["https://storage.googleapis.com/persi-server/test_file.wav", "https://storage.googleapis.com/persi-server/test_file.wav"])
    profile_image: Optional[str] = Field(None, example="https://storage.googleapis.com/persi-server/test_file.jpg")
    register_number: Optional[int] = Field(None, example=0)

class RegisterSpeaker(BaseModel):
    speaker_id: str = Field(None, example="id")