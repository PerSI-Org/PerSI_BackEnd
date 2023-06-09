from typing import List
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from bson.objectid import ObjectId
from typing import Dict
from server.models.speaker import Speaker, SpeakerUpdate
from server.models import mongodb
from server.config import MONGO_DB_NAME, MONGO_DB_URL
from google.cloud import storage
import yaml
import numpy as np
import torch
import soundfile as sf
from server.Wav2vec_model.example.classification import train
from server.pyannote_audio_model.speaker_diarization_for_data import speaker_diarization_for_data
import os
from pydub import AudioSegment
from scipy.io import wavfile

client = storage.Client.from_service_account_json(
    "persi-server-34f8d30f4227.json")
bucket_name = "persi-bucket"
bucket = client.bucket(bucket_name)


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


async def register_speaker_to_model(speaker: Speaker):
    if speaker is None:
        raise Exception("Speaker not found")

    parent_directory = os.path.dirname(
        os.path.dirname(os.path.abspath(__file__)))

    # Get voice sample from GCP
    source_blob_name = speaker.voice_sample.split("/")[-1]

    speakers = await mongodb.engine.find(Speaker)
    # Count spakers length
    current_speakers_count = len(speakers)
    # Temporary location
    destination_file_name = parent_directory + \
        f"/Wav2vec_model/src/data/{current_speakers_count - 1}/{speaker.id}.flac"

    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)

    convert_file_to_flac(destination_file_name)

    # Load and convert voice sample to a format suitable for Wav2Vec
    data, samplerate = sf.read(destination_file_name)
    if samplerate != 16000:
        raise Exception("Sample rate should be 16000")

    # Load the current yaml file
    with open(parent_directory+"/Wav2vec_model/src/config/clf.config.yaml", 'r') as stream:
        data_loaded = yaml.safe_load(stream)

    # Update out_dim in yaml file
    data_loaded['classification']['Model2']['out_dim'] = current_speakers_count
    with open(parent_directory+"/Wav2vec_model/src/config/clf.config.yaml", 'w') as yaml_file:
        yaml.dump(data_loaded, yaml_file)

    # Create train set and train the model
    train()

    return {"message": f"Successfully registered and trained speaker {speaker.id}"}

# 통화 녹음 파일들을 GCP 버킷에서 불러와서 하나의 화자의 목소리로 변형해 등록하는 함수.


async def concat_speaker_call_data(speaker: Speaker):

    parent_directory = os.path.dirname(
        os.path.dirname(os.path.abspath(__file__)))

    # Get voice samples from GCP
    source_blob_names = [url.split("/")[-1] for url in speaker.call_samples]
    destination_file_names = []

    bucket = client.bucket(bucket_name)

    for i, source_blob_name in enumerate(source_blob_names):
        destination_file_name = parent_directory + f"/tmp/{speaker.id}_{i}.m4a"
        destination_file_names.append(destination_file_name)
        blob = bucket.blob(source_blob_name)
        blob.download_to_filename(destination_file_name)

    # Convert voice sample using speaker_diarization_for_data function
    data_out_dir = parent_directory + "/tmp"
    concat_filename = f"{speaker.id}_concated"

    for data_in_dir in destination_file_name:
        speaker_diarization_for_data(
            data_in_dir, data_out_dir, concat_filename)

    # 업로드할 파일 경로
    concated_audio_file_path = os.path.join(data_out_dir, concat_filename)

    blob_result = bucket.blob(concat_filename)

    # 분리된 오디오 파일을 버킷에 업로드
    blob_result.upload_from_filename(concated_audio_file_path)

    # 업로드된 파일의 공개 URL 생성
    url = f"https://storage.googleapis.com/{bucket_name}/{concat_filename}"

    speaker.voice_sample = url

    updated_speaker = await mongodb.engine.save(speaker)

    return updated_speaker


def convert_file_to_flac(file_path: str, target_format="flac") -> str:
    audio = AudioSegment.from_file(file_path)

    # Change sample rate to 16000Hz
    audio = audio.set_frame_rate(16000)
    audio = audio.set_channels(1)

    # Save as flac
    flac_path = file_path.rsplit(".", 1)[0] + f".{target_format}"
    audio.export(flac_path, format=target_format)

    return flac_path
