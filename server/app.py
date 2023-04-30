from fastapi import FastAPI, Form
from server.models import mongodb
from server.controller import speaker_controller
from server.controller.speaker_controller import router as speaker_router

app = FastAPI()


@app.on_event("startup")
def on_app_start():
    mongodb.connect()


@app.on_event("shutdown")
async def on_app_shutdown():
    mongodb.close()

app.include_router(speaker_router)
