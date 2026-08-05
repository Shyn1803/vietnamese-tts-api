# Vietnamese TTS API

Dịch vụ **Text-to-Speech tiếng Việt chạy local** bằng **VieNeu-TTS v3 Turbo**, **FastAPI**, **Docker Compose** và **NVIDIA GPU**.

API được triển khai nội bộ tại:

```text
http://10.1.53.88:8081
```

Model mặc định:

```text
pnnbao-ump/VieNeu-TTS-v3-Turbo
```

## 1. Tính năng

- Chuyển văn bản tiếng Việt thành file âm thanh WAV.
- Chạy inference bằng NVIDIA GPU trong Docker.
- Xác thực bằng Bearer API key.
- Cung cấp Swagger để kiểm tra API.
- Cung cấp endpoint health check và danh sách giọng đọc.
- Thiết kế endpoint gần tương thích với OpenAI Audio Speech API.

## 2. Yêu cầu hệ thống

Server cần có:

- Linux.
- Docker Engine.
- Docker Compose.
- NVIDIA GPU và driver phù hợp.
- NVIDIA Container Toolkit.
- Kết nối Internet trong lần đầu tải model từ Hugging Face.

Kiểm tra môi trường:

```bash
nvidia-smi
docker --version
docker compose version
```

Kiểm tra Docker truy cập được GPU:

```bash
docker run --rm --gpus all nvidia/cuda:12.8.1-base-ubuntu22.04 nvidia-smi
```

## 3. Cấu hình môi trường

Tạo file `.env` từ file mẫu:

```bash
cp .env.example .env
nano .env
```

Ví dụ:

```env
TTS_PORT=8081
TTS_API_KEY=THAY_BANG_API_KEY_DAI_VA_KHO_DOAN
TTS_DEFAULT_VOICE=Ngọc Linh
TTS_MAX_TEXT_LENGTH=5000
NVIDIA_VISIBLE_DEVICES=all
```

Không commit file `.env` lên Git.

## 4. Khởi chạy dịch vụ

Build và chạy container:

```bash
docker compose up -d --build
```

Xem trạng thái:

```bash
docker compose ps
```

Theo dõi log:

```bash
docker compose logs -f tts-api
```

Model sẽ được tải ở lần chạy đầu và lưu trong Docker volume cache của Hugging Face. Vì vậy lần khởi động đầu tiên có thể lâu hơn các lần sau.

## 5. Các endpoint

| Method | Endpoint | Mục đích |
|---|---|---|
| `GET` | `/health` | Kiểm tra trạng thái dịch vụ |
| `GET` | `/docs` | Swagger UI |
| `GET` | `/v1/models` | Danh sách model |
| `GET` | `/v1/voices` | Danh sách giọng đọc |
| `POST` | `/v1/audio/speech` | Chuyển văn bản thành âm thanh |

Swagger:

```text
http://10.1.53.88:8081/docs
```

## 6. Kiểm tra health check

### Linux hoặc macOS

```bash
curl http://10.1.53.88:8081/health
```

### Windows PowerShell

PowerShell ánh xạ `curl` thành `Invoke-WebRequest`, vì vậy nên dùng `curl.exe` hoặc `Invoke-RestMethod`:

```powershell
curl.exe http://10.1.53.88:8081/health
```

Hoặc:

```powershell
Invoke-RestMethod http://10.1.53.88:8081/health
```

Kết quả mong đợi:

```json
{
  "status": "ok",
  "model": "pnnbao-ump/VieNeu-TTS-v3-Turbo"
}
```

## 7. Danh sách giọng hỗ trợ

Các giọng hiện có:

```text
Minh Đức
Phạm Tuyên
Thái Sơn
Xuân Vĩnh
Thanh Bình
Trúc Ly
Ngọc Linh
Đoan Trang
Mai Anh
Thục Đoan
Minh Triết
Thùy Dung
Quang Sơn
Ngọc Trân
```

Kiểm tra trực tiếp từ API:

```bash
curl http://10.1.53.88:8081/v1/voices \
  -H "Authorization: Bearer YOUR_API_KEY"
```

Không sử dụng các tên giọng không có trong danh sách, ví dụ `Ngọc Lan` hoặc `Bình An`.

## 8. Sinh âm thanh bằng Linux hoặc macOS

```bash
curl -X POST http://10.1.53.88:8081/v1/audio/speech \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "pnnbao-ump/VieNeu-TTS-v3-Turbo",
    "input": "Xin chào, đây là hệ thống chuyển văn bản thành giọng nói tiếng Việt.",
    "voice": "Ngọc Linh",
    "response_format": "wav",
    "speed": 1.0
  }' \
  --output speech.wav
```

## 9. Sinh âm thanh bằng Windows PowerShell

Dùng `Invoke-WebRequest` để tránh lỗi escape JSON:

```powershell
$body=@{input="Xin chào, đây là hệ thống chuyển văn bản thành giọng nói tiếng Việt.";voice="Ngọc Linh";response_format="wav";speed=1.0}|ConvertTo-Json; Invoke-WebRequest -Uri "http://10.1.53.88:8081/v1/audio/speech" -Method POST -Headers @{Authorization="Bearer YOUR_API_KEY"} -ContentType "application/json; charset=utf-8" -Body ([System.Text.Encoding]::UTF8.GetBytes($body)) -OutFile "speech.wav"
```

Mở file kết quả:

```powershell
Start-Process .\speech.wav
```

## 10. Gọi API bằng Python

Cài thư viện:

```bash
pip install requests
```

Ví dụ:

```python
from pathlib import Path

import requests

API_URL = "http://10.1.53.88:8081/v1/audio/speech"
API_KEY = "YOUR_API_KEY"

response = requests.post(
    API_URL,
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json; charset=utf-8",
    },
    json={
        "model": "pnnbao-ump/VieNeu-TTS-v3-Turbo",
        "input": "Xin chào, đây là nội dung cần chuyển thành giọng nói.",
        "voice": "Ngọc Linh",
        "response_format": "wav",
        "speed": 1.0,
    },
    timeout=600,
)

response.raise_for_status()
Path("speech.wav").write_bytes(response.content)
```

## 11. Gọi API bằng Node.js hoặc TypeScript

API key phải được lưu ở backend, không hard-code trong frontend trình duyệt.

```ts
import { writeFile } from "node:fs/promises";

const apiUrl = "http://10.1.53.88:8081/v1/audio/speech";
const apiKey = process.env.TTS_API_KEY;

if (!apiKey) {
  throw new Error("Missing TTS_API_KEY");
}

const response = await fetch(apiUrl, {
  method: "POST",
  headers: {
    Authorization: `Bearer ${apiKey}`,
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    model: "pnnbao-ump/VieNeu-TTS-v3-Turbo",
    input: "Xin chào, đây là nội dung cần chuyển thành giọng nói.",
    voice: "Ngọc Linh",
    response_format: "wav",
    speed: 1.0,
  }),
});

if (!response.ok) {
  throw new Error(`TTS API error ${response.status}: ${await response.text()}`);
}

const audio = Buffer.from(await response.arrayBuffer());
await writeFile("speech.wav", audio);
```

## 12. Kiểm tra GPU trong lúc sinh âm thanh

Mở một terminal khác trên server:

```bash
watch -n 1 nvidia-smi
```

Sau đó gọi endpoint `/v1/audio/speech`. Trong lúc inference, tiến trình Python phải xuất hiện và VRAM có thể tăng.

## 13. Khởi động lại và cập nhật

Khởi động lại container:

```bash
docker compose restart tts-api
```

Build lại sau khi sửa code hoặc dependency:

```bash
docker compose down
docker compose build --no-cache
docker compose up -d
```

Xem 200 dòng log gần nhất:

```bash
docker compose logs --tail=200 tts-api
```

## 14. Các lỗi thường gặp

### `401 Unauthorized`

Nguyên nhân:

- Thiếu header `Authorization`.
- API key không đúng.
- Giá trị `TTS_API_KEY` trong `.env` đã thay đổi nhưng container chưa được restart.

Header đúng:

```text
Authorization: Bearer YOUR_API_KEY
```

### `422 Unprocessable Entity`

Nguyên nhân thường gặp:

- Body không phải JSON hợp lệ.
- Thiếu trường `input`.
- PowerShell escape JSON sai.
- Kiểu dữ liệu của `speed` không đúng.

Nên dùng ví dụ PowerShell bằng `Invoke-WebRequest` trong README này.

### `Voice not found`

Tên giọng không nằm trong danh sách hỗ trợ. Gọi `/v1/voices` để lấy danh sách chính xác.

### Lần đầu gọi API rất lâu

Model có thể đang được tải từ Hugging Face hoặc đang khởi tạo trên GPU. Theo dõi bằng:

```bash
docker compose logs -f tts-api
```

### Container không nhận GPU

Kiểm tra:

```bash
docker run --rm --gpus all nvidia/cuda:12.8.1-base-ubuntu22.04 nvidia-smi
```

Nếu lệnh này lỗi, cần kiểm tra NVIDIA driver và NVIDIA Container Toolkit trên host.

## 15. Bảo mật triển khai

- Không hard-code API key trong source code hoặc frontend.
- Không commit `.env` lên Git.
- Nếu chỉ dùng nội bộ, nên giới hạn truy cập theo dải IP.
- Nếu mở qua Internet, nên đặt NGINX hoặc API Gateway phía trước.
- Bật HTTPS khi truyền dữ liệu ngoài mạng nội bộ.
- Có thể bổ sung rate limit, audit log và giới hạn độ dài văn bản.
- Nên thay API key nếu key đã xuất hiện trong log, ảnh chụp hoặc nội dung chia sẻ.

## 16. Lưu ý về hiệu năng

- Chỉ nên chạy một worker inference trên một GPU nếu ứng dụng chưa có cơ chế điều phối hàng đợi.
- Nhiều request đồng thời có thể làm tăng VRAM hoặc gây lỗi out-of-memory.
- Với tải cao, nên đặt Redis Queue hoặc hệ thống job queue phía trước worker TTS.
- Văn bản dài nên được chia thành các đoạn hợp lý và ghép audio nếu model xử lý không ổn định.
