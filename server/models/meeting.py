from odmantic import Model, ObjectId
from typing import Optional, Dict, Union
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime
import odmantic


class Meeting(Model):
    name: str
    description: str
    audio_files: Optional[List[str]]
    conversation_file: Optional[str]
    owner_id: ObjectId
    speakers_id: Optional[List[ObjectId]]
    created_at: Optional[str]
    conversations: Optional[List[Dict[str, Union[str, float]]]]


class MeetingCreate(BaseModel):
    name: str = Field(None, example="음성인식 1차 회의")
    description: str = Field(None, example="음성인식 1차 회의록")
    owner_id: str

class AllMeetings(BaseModel):
    id: str
    name: str = Field(None, example="음성인식 1차 회의")
    description: str
    audio_files: Optional[List[str]]
    conversation_file: Optional[str]
    owner_id: str
    speakers_name: List[str]
    speakers_image: Optional[List[str | None]]
    speakers_id: List[str]
    created_at: Optional[str]

class ConcatAudioFile(BaseModel):
    audio_file_url: str = Field(None, example="https://storage.googleapis.com/persi-server/test_file.wav")

class MeetingUpdate(BaseModel):
    name: Optional[str] = Field(None, example="음성인식 1차 회의")
    description: Optional[str] = Field(None, example="음성인식 1차 회의록")
    speakers_id: Optional[List[str]] = Field(None, example=["id"])
    conversation_file: Optional[str] = Field(None, example="https://storage.googleapis.com/persi-server/test_file.wav")
    conversations: Optional[List[Dict[str, Union[str, float]]]] = Field(None, example=[{
            "speaker": "SPEAKER_01",
            "start_time": 1.11,
            "stop_time": 3.11,
            "script": "Hello, World!"
        }])
