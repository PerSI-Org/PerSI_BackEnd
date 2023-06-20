from fastapi import UploadFile, File, HTTPException
from fastapi import FastAPI, File, UploadFile
from server.models import mongodb
from server.controller import speaker_controller
from server.controller.speaker_controller import router as speaker_router
from server.controller.user_controller import router as user_router
from server.controller.meetting_controller import router as meeting_router
from google.cloud import storage
from typing import List
from pydantic import BaseModel
from datetime import datetime

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
    current_time = datetime.now().strftime("%Y%m%d%H%M%S")
    sanitized_filename = file.filename.replace(" ", "")
    blob = bucket.blob(f"{current_time}{file.filename}")
    blob.upload_from_file(file.file)
    url = f"https://storage.googleapis.com/{bucket_name}/{current_time}{sanitized_filename}"
    return {"file_url": url}


@app.post("/uploadfiles/")
async def create_upload_files(files: List[UploadFile]):
    current_time = datetime.now().strftime("%Y%m%d%H%M%S")
    urls = []
    for file in files:
        try:
            sanitized_filename = file.filename.replace(" ", "")
            blob = bucket.blob(f"{current_time}{file.filename}")
            blob.upload_from_file(file.file)
            url = f"https://storage.googleapis.com/{bucket_name}/{current_time}{sanitized_filename}"
            urls.append(url)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    return {"file_urls": urls}


app.include_router(speaker_router, prefix="/speakers", tags=["Speaker"])
app.include_router(user_router, prefix="/users", tags=["User"])
app.include_router(meeting_router, prefix="/meetings", tags=["Meeting"])
