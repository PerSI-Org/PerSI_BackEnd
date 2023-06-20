from fastapi import APIRouter, Body, HTTPException
from fastapi.encoders import jsonable_encoder
from typing import List, Optional
from datetime import datetime
from pymongo.errors import DuplicateKeyError
from server.services.speakers import retrieve_speaker
from fastapi.responses import JSONResponse

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
    MeetingCreate,
    AllMeetings,
    ConcatAudioFile
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


@router.get("/", response_description="List all meetings", response_model=List[AllMeetings])
async def get_meetings():
    meetings = await retrieve_meetings()
    speaker_ids = []
    speakers_for_meetings = []

    for meeting in meetings:
        speakers = []
        speaker_ids.extend(meeting.speakers_id)
        for speaker_id in speaker_ids:
            speaker = await retrieve_speaker(speaker_id)
            speakers.append(speaker)
        speakers_for_meetings.append(speakers)
    
    speaker_names=  [[speaker.name for speaker in speakers] for speakers in speakers_for_meetings]
    speaker_images = [[speaker.profile_image for speaker in speakers] for speakers in speakers_for_meetings]
    speakers_id = [[str(speaker.id) for speaker in speakers] for speakers in speakers_for_meetings]

    all_meetings = []
    for meeting, speakers_name, speakers_image, speaker_id in zip(meetings, speaker_names, speaker_images, speakers_id):
        all_meetings.append(
            AllMeetings(
                id=str(meeting.id),
                name=meeting.name,
                description=meeting.description,
                audio_files=meeting.audio_files,
                conversation_file=meeting.conversation_file,
                owner_id=str(meeting.owner_id),
                speakers_name=speakers_name,
                speakers_image=speakers_image,
                speakers_id=speaker_id,
                created_at=meeting.created_at
            )
        )

    return all_meetings


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
        return_meeting = await retrieve_meeting(id)
        return return_meeting
    raise HTTPException(status_code=400, detail="No fields to update")


@router.delete("/{id}", response_description="Delete a meeting")
async def delete_meeting_data(id: str):
    meeting = await retrieve_meeting(id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    await delete_meeting(meeting)
    return {"message": "Meeting deleted successfully"}


@router.post("/meeting/{meeting_id}/audio", response_description="Add audio file path to a meeting")
async def add_audio_file_path(meeting_id: str, data: ConcatAudioFile = Body(...)):
    meeting = await retrieve_meeting(meeting_id)
    url = jsonable_encoder(data)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    updated_meeting = await update_meeting_audio_files(meeting, url["audio_file_url"])
    return updated_meeting


@router.post("/conversation/{meeting_id}")
async def create_conversation(meeting_id: str, response_description="update conversations"):
    meeting = await retrieve_meeting(meeting_id)
    updated_meeting = await infer_conversation(meeting)
    if not updated_meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    meeting = await retrieve_meeting(meeting_id)
    
    return meeting
