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
from server.services.speakers import retrieve_speakers, retrieve_speaker
from datetime import datetime
from pydub import AudioSegment


client = storage.Client.from_service_account_json(
    "persi-server-34f8d30f4227.json")
bucket_name = "persi-bucket"
bucket = client.bucket(bucket_name)


async def add_meeting(meeting: Meeting) -> Meeting:
    try:
        new_meeting = Meeting(**meeting)
        speakers = await retrieve_speakers()
        new_meeting.created_at = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        new_meeting.speakers_id = [speaker.id for speaker in speakers if speaker.user_id == new_meeting.owner_id]
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

    parent_directory = os.path.dirname(
        os.path.dirname(os.path.abspath(__file__)))

    destination_file_name = parent_directory + f"/meeting_tmp/{meeting.id}.wav"
    result_file_directory = parent_directory + f"/meeting_tmp/{meeting.id}"

    if not os.path.exists(result_file_directory):
        os.makedirs(result_file_directory)

    blob = bucket.blob(audio_file_url.split("/")[-1])
    blob.download_to_filename(destination_file_name)
    
    convert_file_to_wav(destination_file_name)

    results = speaker_diarization_for_conversation(
        destination_file_name, result_file_directory)

    print(results)

    urls = []
    
    file_list = os.listdir(result_file_directory)
    for file_name in file_list:
        file_path = os.path.join(result_file_directory, file_name)
        blob_result = bucket.blob(file_name)
        # 분리된 오디오 파일을 버킷에 업로드
        blob_result.upload_from_filename(file_path)
        url = f"https://storage.googleapis.com/{bucket_name}/{file_name}"
        urls.append(url)
        os.remove(file_path)

    meeting.audio_files = urls
    meeting.conversations = results

    os.remove(destination_file_name)

    # 업데이트된 회의 객체 저장
    updated_meeting = await mongodb.engine.save(meeting)

    return updated_meeting


async def infer_conversation(meeting: Meeting) -> List[Dict[str, str]]:

    parent_directory = os.path.dirname(
        os.path.dirname(os.path.abspath(__file__)))

    # Get audio files from GCP
    source_blob_names = [url.split("/")[-1] for url in meeting.audio_files]
    destination_file_names = []

    # Download each file individually
    for i, source_blob_name in enumerate(source_blob_names):
        # Temporary location for each file
        destination_file_name = parent_directory + f"/meeting_tmp/{meeting.id}/speaker_{i}.wav"
        destination_file_names.append(
            destination_file_name)  # store all filenames
        blob = bucket.blob(source_blob_name)
        blob.download_to_filename(destination_file_name)
        convert_file_to_flac(destination_file_name)
        os.remove(destination_file_name)

    # Infer conversation from each audio file
    conversations = meeting.conversations
    speakers_id = meeting.speakers_id
    speakers = []
    for speaker_id in speakers_id:
        speaker = await retrieve_speaker(speaker_id)
        speakers.append(speaker)
    results, speakers = predict(parent_directory + f"/meeting_tmp/{meeting.id}")
    for result, conversation in zip(results, conversations):
        conversation["script"] = result
        last_digit = int(conversation["speaker"].split("_")[-1])
        matching_speaker = next(
            (speaker for speaker in speakers if speaker.register_number == last_digit), None
        )
        if matching_speaker:
            conversation["speaker"] = str(matching_speaker.id)

    meeting.conversations = conversations

    updated_meeting = await mongodb.engine.save(meeting)

    return updated_meeting

def convert_file_to_wav(file_path: str, target_format="wav") -> str:
    audio = AudioSegment.from_file(file_path)

    # Save as wav
    wav_path = file_path.rsplit(".", 1)[0] + f".{target_format}"
    audio.export(wav_path, format=target_format)

    return wav_path

def convert_file_to_flac(file_path: str, target_format="flac") -> str:
    audio = AudioSegment.from_file(file_path)

    # Change sample rate to 16000Hz
    audio = audio.set_frame_rate(16000)
    audio = audio.set_channels(1)

    # Save as flac
    flac_path = file_path.rsplit(".", 1)[0] + f".{target_format}"
    audio.export(flac_path, format=target_format)

    return flac_path