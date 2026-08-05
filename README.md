# Vietnamese TTS API

API Text-to-Speech tiếng Việt chạy local bằng VieNeu-TTS v3 Turbo, FastAPI và NVIDIA GPU.

## 1. Kiểm tra GPU trên server

```bash
nvidia-smi
docker --version
docker compose version
```

Kiểm tra Docker truy cập được GPU:

```bash
docker run --rm --gpus all nvidia/cuda:12.8.1-base-ubuntu22.04 nvidia-smi
```

## 2. Khởi chạy

```bash
cp .env.example .env
nano .env
docker compose up -d --build
docker compose logs -f tts-api
```

Model được tải lần đầu và lưu trong Docker volume `hf-cache`.

## 3. API

Swagger:

```text
http://SERVER_IP:8000/docs
```

Health check:

```bash
curl http://SERVER_IP:8000/health
```

Danh sách giọng:

```bash
curl http://SERVER_IP:8000/v1/voices \
  -H "Authorization: Bearer YOUR_API_KEY"
```

Sinh audio:

```bash
curl -X POST http://SERVER_IP:8000/v1/audio/speech \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "pnnbao-ump/VieNeu-TTS-v3-Turbo",
    "input": "Xin chào, đây là hệ thống chuyển văn bản thành giọng nói tiếng Việt.",
    "voice": "Ngọc Lan",
    "response_format": "wav",
    "speed": 1.0
  }' \
  --output speech.wav
```

## 4. Gọi từ Python

```python
import requests

response = requests.post(
    "http://SERVER_IP:8000/v1/audio/speech",
    headers={"Authorization": "Bearer YOUR_API_KEY"},
    json={
        "model": "pnnbao-ump/VieNeu-TTS-v3-Turbo",
        "input": "Nội dung cần chuyển thành giọng nói.",
        "voice": "Bình An",
        "response_format": "wav",
        "speed": 1.0,
    },
    timeout=300,
)
response.raise_for_status()
open("speech.wav", "wb").write(response.content)
```

## 5. Gọi từ JavaScript/TypeScript

```ts
const response = await fetch("http://SERVER_IP:8000/v1/audio/speech", {
  method: "POST",
  headers: {
    Authorization: `Bearer ${process.env.TTS_API_KEY}`,
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    model: "pnnbao-ump/VieNeu-TTS-v3-Turbo",
    input: "Nội dung cần chuyển thành giọng nói.",
    voice: "Ngọc Lan",
    response_format: "wav",
    speed: 1.0,
  }),
});

if (!response.ok) throw new Error(await response.text());
const audio = Buffer.from(await response.arrayBuffer());
```

## 6. Bảo mật triển khai

Không nên mở trực tiếp cổng 8000 ra Internet. Nên đặt NGINX/Ingress phía trước, bật HTTPS, giới hạn IP nội bộ và giữ API key trong biến môi trường của project gọi API.
