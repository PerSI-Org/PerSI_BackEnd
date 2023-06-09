from fastapi import APIRouter, Body, HTTPException
from fastapi.encoders import jsonable_encoder
from typing import List, Optional
from datetime import datetime
from pymongo.errors import DuplicateKeyError

from server.services.meetings import (
    add_meeting,
    delete_meeting,
    retrieve_meeting,
    retrieve_meetings,
    update_meeting,
    update_meeting_audio_files,
    infer_conversation
)
from server.models.meeting import (
    Meeting,
    MeetingUpdate,
    MeetingCreate
)

router = APIRouter()


@router.post("/", response_description="Add new meeting", response_model=Meeting)
async def create_meeting(meeting: MeetingCreate = Body(...)):
    meeting = jsonable_encoder(meeting)
    try:
        new_meeeting = await add_meeting(meeting)
        return new_meeeting
    except DuplicateKeyError:
        raise HTTPException(
            status_code=400, detail="This meeting is already exist."
        )


@router.get("/", response_description="List all meetings", response_model=List[Meeting])
async def get_meetings():
    meetings = await retrieve_meetings()
    return meetings


@router.get("/{id}", response_description="Get a single meeting", response_model=Meeting)
async def get_meeting(id: str):
    meeting = await retrieve_meeting(id)
    if meeting:
        return meeting
    raise HTTPException(status_code=404, detail="Meeting not found")


@router.put("/{id}", response_description="Update a meeting", response_model=Meeting)
async def update_meeting_data(id: str, data: MeetingUpdate = Body(...)):
    data = {k: v for k, v in data.dict(
        exclude_unset=True).items() if v is not None}
    if len(data) >= 1:
        meeting = await retrieve_meeting(id)
        if not meeting:
            raise HTTPException(status_code=404, detail="Meeting not found")
        updated_meeting = await update_meeting(meeting, data)
        return update_meeting
    raise HTTPException(status_code=400, detail="No fields to update")


@router.delete("/{id}", response_description="Delete a meeting")
async def delete_meeting_data(id: str):
    meeting = await retrieve_meeting(id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    await delete_meeting(meeting)
    return {"message": "Meeting deleted successfully"}


@router.post("/meeting/{meeting_id}/audio", response_description="Add audio file path to a meeting")
async def add_audio_file_path(meeting_id: str, audio_file_path: str):
    meeting = await retrieve_meeting(meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    updated_meeting = await update_meeting_audio_files(meeting, audio_file_path)
    return updated_meeting


@router.post("/conversation/{meeting_id}")
async def create_conversation(meeting_id: str):
    conversation = await infer_conversation(meeting_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Meeting not found")

    return conversation
