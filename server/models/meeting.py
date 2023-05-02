from odmantic import Model, ObjectId
from typing import Optional
from pydantic import BaseModel, Field
from typing import List


class Meeting(Model):
    name: str
    description: str
    owner_id: ObjectId
    speakers_id: List[ObjectId]


class MeetingCreate(BaseModel):
    name: str = Field(None, example="김지우")
    description: str = Field(None, example="example@goolge.com")
    speakers_id: List[str]


class MeetingUpdate(BaseModel):
    name: Optional[str] = Field(None, example="김지우")
    description: Optional[str] = Field(None, example="example@goolge.com")
    speakers_id: List[ObjectId]
