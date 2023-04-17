from server.models import mongodb
from server.models.speaker import Speaker

# 회원 가입


async def create_speaker(name: str, profile_img: str) -> Speaker:
    speaker = Speaker(name=name, profile_img=profile_img)
    await mongodb.engine.save(speaker)
    print(f"{name}으로 가입되었습니다.")
    return speaker
