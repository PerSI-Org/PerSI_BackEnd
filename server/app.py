from fastapi import FastAPI, Form
from server.models import mongodb
from server.controller import speaker_controller

app = FastAPI()


@app.on_event("startup")
def on_app_start():
    mongodb.connect()


@app.on_event("shutdown")
async def on_app_shutdown():
    mongodb.close()


@app.post("/speaker/create")
async def create_speaker(name: str = Form(), profile_img: str = Form()):
    print(name, profile_img)
    speaker = await speaker_controller.create_speaker(name=name, profile_img=profile_img)
    return speaker
