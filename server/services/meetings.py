import urllib.request
from server.models.meeting import Meeting
import os
import subprocess
from typing import List, Dict
from pymongo.errors import PyMongoError
from bson.objectid import ObjectId
from server.models.meeting import Meeting, MeetingUpdate
from server.models import mongodb
from google.cloud import storage
from server.Wav2vec_model.example.classification import predict
from server.pyannote_audio_model.speaker_diarization_for_conversation import speaker_diarization_for_conversation

client = storage.Client.from_service_account_json(
    "persi-server-34f8d30f4227.json")
bucket_name = "persi-bucket"
bucket = client.bucket(bucket_name)


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


async def update_meeting_audio_files(meeting: Meeting, audio_file_url: str) -> Meeting:

    destination_file_name = f"meeting_tmp/{meeting.id}.wav"
    result_file_directory = f"meeting_tmp/{meeting.id}"

    blob = bucket.blob(audio_file_url)
    blob.download_to_filename(destination_file_name)

    speaker_diarization_for_conversation(
        destination_file_name, result_file_directory)

    meeting.audio_files = [url]

    # 업데이트된 회의 객체 저장
    updated_meeting = await meeting.save()

    return updated_meeting


async def infer_conversation(meeting_id: str) -> List[Dict[str, str]]:
    # Get meeting from MongoDB
    meeting = await mongodb.engine.find_one(Meeting, Meeting.id == ObjectId(id))

    # Get audio files from GCP
    source_blob_names = meeting['audio_files']  # assuming this is a list
    destination_file_names = []

    # Download each file individually
    for i, source_blob_name in enumerate(source_blob_names):
        # Temporary location for each file
        destination_file_name = f"meeting_tmp/{meeting_id}_{i}.wav"
        destination_file_names.append(
            destination_file_name)  # store all filenames
        blob = bucket.blob(source_blob_name)
        blob.download_to_filename(destination_file_name)

    # Infer conversation from each audio file
    conversation = []
    for audio_file in destination_file_names:
        # Use your predict function here
        # assuming your function returns a list of transcriptions and speakers
        results, speakers = predict()
        for result, speaker in zip(results, speakers):
            conversation.append({
                # Assuming speakers are names. If they are IDs, use a lookup to get names.
                "speaker": speaker,
                "start_time": "00:00",  # To add start_time, you will need to modify your predict function
                "script": result
            })

    return conversation
