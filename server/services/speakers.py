from typing import List
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from bson.objectid import ObjectId
from typing import Dict
from server.models.speaker import Speaker, SpeakerUpdate
from server.models import mongodb as client
from server.config import MONGO_DB_NAME, MONGO_DB_URL
from server.models import mongodb


async def add_speaker(speaker: Speaker) -> Speaker:
    try:
        new_speaker = Speaker(**speaker)
        await mongodb.engine.save(new_speaker)
        return new_speaker
    except PyMongoError as e:
        raise ValueError(f"Error occurred while adding the speaker: {str(e)}")


async def retrieve_speaker(id: str) -> Speaker:
    try:
        speaker = await mongodb.engine.find_one(Speaker, Speaker.id == ObjectId(id))
        return speaker
    except PyMongoError as e:
        raise ValueError(
            f"Error occurred while retrieving the speaker: {str(e)}")


async def retrieve_speakers() -> List[Speaker]:
    try:
        speakers = []
        async for speaker in mongodb.engine.find(Speaker):
            print(speaker)
            speakers.append(speaker)
        return speakers
    except PyMongoError as e:
        raise ValueError(
            f"Error occurred while retrieving the speakers: {str(e)}")


async def update_speaker(speaker: Speaker, data: SpeakerUpdate) -> Speaker:
    try:
        for field, value in data.items():
            if value is not None:
                setattr(speaker, field, value)
        updated_speaker = await mongodb.engine.save(
            speaker
        )
        if updated_speaker:
            return updated_speaker
    except PyMongoError as e:
        raise ValueError(
            f"Error occurred while updating the speaker: {str(e)}")


async def delete_speaker(speaker: Speaker):
    try:
        await mongodb.engine.delete(speaker)
    except PyMongoError as e:
        raise ValueError(
            f"Error occurred while deleting the speaker: {str(e)}")
