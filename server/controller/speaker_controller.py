from fastapi import APIRouter, Body, HTTPException
from fastapi.encoders import jsonable_encoder
from typing import List, Optional
from datetime import datetime
from pymongo.errors import DuplicateKeyError

from server.services.speakers import (
    add_speaker,
    delete_speaker,
    retrieve_speaker,
    retrieve_speakers,
    update_speaker,
    register_speaker_to_model,
    concat_speaker_call_data
)
from server.models.speaker import (
    Speaker,
    SpeakerUpdate,
    SpeakerCreate
)

router = APIRouter()


@router.post("/", response_description="Add new speaker", response_model=Speaker)
async def create_speaker(speaker: SpeakerCreate = Body(...)):
    speaker = jsonable_encoder(speaker)
    try:
        new_speaker = await add_speaker(speaker)
        return new_speaker
    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail="This name already exists")


@router.get("/", response_description="List all speakers", response_model=List[Speaker])
async def get_speakers():
    speakers = await retrieve_speakers()
    return speakers


@router.get("/{id}", response_description="Get a single speaker", response_model=Speaker)
async def get_speaker(id: str):
    speaker = await retrieve_speaker(id)
    if speaker:
        return speaker
    raise HTTPException(status_code=404, detail="Speaker not found")


@router.put("/{id}", response_description="Update a speaker", response_model=Speaker)
async def update_speaker_data(id: str, data: SpeakerUpdate = Body(...)):
    data = {k: v for k, v in data.dict(
        exclude_unset=True).items() if v is not None}
    if len(data) >= 1:
        speaker = await retrieve_speaker(id)
        if not speaker:
            raise HTTPException(status_code=404, detail="Speaker not found")
        updated_speaker = await update_speaker(speaker, data)
        return updated_speaker
    raise HTTPException(status_code=400, detail="No fields to update")


@router.delete("/{id}", response_description="Delete a speaker")
async def delete_speaker_data(id: str):
    speaker = await retrieve_speaker(id)
    if not speaker:
        raise HTTPException(status_code=404, detail="Speaker not found")
    await delete_speaker(speaker)
    return {"message": "Speaker deleted successfully"}


@router.post("/register_speaker")
async def register_speaker(speaker_id: str):
    try:
        speaker = await retrieve_speaker(speaker_id)
        return await register_speaker_to_model(speaker)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("concat_call_data")
async def concat_call_data(speaker_id: str):
    try:
        speaker = await retrieve_speaker(speaker_id)
        return await concat_speaker_call_data(speaker)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
