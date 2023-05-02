from fastapi import FastAPI, File, UploadFile
from server.models import mongodb
from server.controller import speaker_controller
from server.controller.speaker_controller import router as speaker_router
from server.controller.user_controller import router as user_router
from google.cloud import storage
from typing import Optional, BinaryIO, Annotated
from pydantic import BaseModel

app = FastAPI()

client = storage.Client.from_service_account_json(
    "persi-server-34f8d30f4227.json")
bucket_name = "persi-bucket"
bucket = client.bucket(bucket_name)


@app.on_event("startup")
def on_app_start():
    mongodb.connect()


@app.on_event("shutdown")
async def on_app_shutdown():
    mongodb.close()


@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    blob = bucket.blob(file.filename)
    blob.upload_from_file(file.file)
    url = f"https://storage.googleapis.com/{bucket_name}/{file.filename}"
    return {"url": url}

app.include_router(speaker_router, prefix="/speakers", tags=["Speaker"])
app.include_router(user_router, prefix="/users", tags=["User"])
