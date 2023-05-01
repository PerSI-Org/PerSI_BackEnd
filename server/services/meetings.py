from typing import List, Dict
from pymongo.errors import PyMongoError
from bson.objectid import ObjectId
from server.models.meeting import Meeting, MeetingUpdate
from server.models import mongodb


async def add_meeting(meeting: Meeting) -> Meeting:
    try:
        new_meeting = Meeting(**meeting)
        await mongodb.engine.save(new_meeting)
        return new_meeting
    except PyMongoError as e:
        raise ValueError(f"Error occurred while adding the speaker: {str(e)}")


async def retrieve_meeting(id: str) -> Meeting:
    try:
        meeting = await mongodb.engine.find_one(Meeting, Meeting.id == ObjectId(id))
        return meeting
    except PyMongoError as e:
        raise ValueError(
            f"Error occurred while retrieving the speaker: {str(e)}")


async def retrieve_meetings() -> List[Meeting]:
    try:
        meetings = []
        async for meeting in mongodb.engine.find(Meeting):
            meetings.append(meeting)
        return meetings
    except PyMongoError as e:
        raise ValueError(
            f"Error occurred while retrieving the speakers: {str(e)}"
        )


async def update_meeting(meeting: Meeting, data: MeetingUpdate) -> Meeting:
    try:
        for field, value in data.items():
            if value is not None:
                setattr(meeting, field, value)
        updated_meeting = await mongodb.engine.save(meeting)
        if updated_meeting:
            return updated_meeting
    except PyMongoError as e:
        raise ValueError(
            f"Error occurred while updating the meeting: {str(e)}")


async def delete_meeting(meeting: Meeting):
    try:
        await mongodb.engine.delete(meeting)
    except PyMongoError as e:
        raise ValueError(
            f"Error occurred while deleting the meeting: {str(e)}")
