import asyncio
import os
import tempfile
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from vieneu import Vieneu

API_KEY = os.getenv("TTS_API_KEY", "")
DEFAULT_VOICE = os.getenv("TTS_DEFAULT_VOICE", "Ngọc Lan")
MAX_TEXT_LENGTH = int(os.getenv("TTS_MAX_TEXT_LENGTH", "5000"))

_tts: Vieneu | None = None
_inference_lock = asyncio.Lock()


@asynccontextmanager
async def lifespan(_: FastAPI):
    global _tts
    # SDK tự phát hiện CUDA và dùng backend PyTorch trên máy có GPU.
    _tts = Vieneu()
    yield
    _tts = None


app = FastAPI(
    title="Vietnamese TTS API",
    version="1.0.0",
    description="Local Vietnamese text-to-speech service powered by VieNeu-TTS v3 Turbo.",
    lifespan=lifespan,
)


class SpeechRequest(BaseModel):
    model: str = Field(default="pnnbao-ump/VieNeu-TTS-v3-Turbo")
    input: str = Field(min_length=1)
    voice: str = Field(default=DEFAULT_VOICE)
    response_format: Literal["wav"] = "wav"
    speed: float = Field(default=1.0, ge=0.25, le=4.0)


def verify_api_key(authorization: str | None = Header(default=None)) -> None:
    if not API_KEY:
        return
    expected = f"Bearer {API_KEY}"
    if authorization != expected:
        raise HTTPException(status_code=401, detail="Invalid API key")


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok" if _tts is not None else "starting",
        "model": "pnnbao-ump/VieNeu-TTS-v3-Turbo",
    }


@app.get("/v1/voices", dependencies=[Depends(verify_api_key)])
def voices() -> dict:
    if _tts is None:
        raise HTTPException(status_code=503, detail="Model is not ready")
    return {
        "data": [
            {"name": label, "id": voice_id}
            for label, voice_id in _tts.list_preset_voices()
        ]
    }


@app.get("/v1/models", dependencies=[Depends(verify_api_key)])
def models() -> dict:
    return {
        "data": [
            {
                "id": "pnnbao-ump/VieNeu-TTS-v3-Turbo",
                "object": "model",
                "sample_rate": 48000,
                "language": ["vi", "en"],
            }
        ]
    }


@app.post("/v1/audio/speech", dependencies=[Depends(verify_api_key)])
async def create_speech(payload: SpeechRequest) -> FileResponse:
    if _tts is None:
        raise HTTPException(status_code=503, detail="Model is not ready")
    if len(payload.input) > MAX_TEXT_LENGTH:
        raise HTTPException(
            status_code=413,
            detail=f"Input exceeds TTS_MAX_TEXT_LENGTH={MAX_TEXT_LENGTH}",
        )
    if payload.speed != 1.0:
        raise HTTPException(
            status_code=422,
            detail="VieNeu SDK currently does not expose speech-speed control; use speed=1.0",
        )

    fd, output_path = tempfile.mkstemp(prefix="tts-", suffix=".wav")
    os.close(fd)

    try:
        # Khóa để tránh nhiều request cùng chiếm GPU và gây OOM.
        async with _inference_lock:
            audio = await asyncio.to_thread(
                _tts.infer,
                payload.input,
                voice=payload.voice,
            )
            await asyncio.to_thread(_tts.save, audio, output_path)
    except Exception as exc:
        Path(output_path).unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=f"TTS generation failed: {exc}") from exc

    return FileResponse(
        output_path,
        media_type="audio/wav",
        filename="speech.wav",
        background=DeleteFileTask(output_path),
    )


class DeleteFileTask:
    def __init__(self, path: str):
        self.path = path

    async def __call__(self) -> None:
        Path(self.path).unlink(missing_ok=True)
