from __future__ import annotations

import os
import sys
from pathlib import Path

import requests

API_URL = os.getenv("TTS_API_URL", "http://10.1.53.88:8081/v1/audio/speech")
API_KEY = os.getenv("TTS_API_KEY", "YOUR_API_KEY")
OUTPUT_DIR = Path("tts-voices")

VOICES = [
    "Minh Đức", "Phạm Tuyên", "Thái Sơn", "Xuân Vĩnh", "Thanh Bình",
    "Trúc Ly", "Ngọc Linh", "Đoan Trang", "Mai Anh", "Thục Đoan",
    "Minh Triết", "Thùy Dung", "Quang Sơn", "Ngọc Trân",
]

LESSON_TEXT = """
Xin chào các bạn. Trong bài học hôm nay, chúng ta sẽ tìm hiểu cách xây dựng một kế hoạch học tập hiệu quả và duy trì tiến độ trong thời gian dài.

Trước tiên, bạn cần xác định rõ mục tiêu muốn đạt được. Mục tiêu nên cụ thể, có thể đo lường và có thời hạn hoàn thành. Ví dụ, thay vì đặt mục tiêu chung chung là học lập trình, bạn có thể đặt mục tiêu hoàn thành kiến thức Python cơ bản trong bốn tuần và xây dựng được một chương trình quản lý nhân viên đơn giản.

Sau khi có mục tiêu, hãy chia mục tiêu lớn thành những nhiệm vụ nhỏ. Mỗi ngày, bạn chỉ nên tập trung vào một hoặc hai nội dung chính. Khi học một kiến thức mới, hãy dành thời gian đọc lý thuyết, xem ví dụ và tự viết lại chương trình bằng cách hiểu của mình. Không nên chỉ sao chép mã nguồn vì cách học đó khiến bạn khó ghi nhớ và khó xử lý khi gặp một bài toán khác.

Tiếp theo, hãy thực hành ngay sau mỗi phần lý thuyết. Ví dụ, khi học về biến, kiểu dữ liệu và câu lệnh điều kiện, bạn có thể viết chương trình tính điểm trung bình và xếp loại học sinh. Khi học về vòng lặp, bạn có thể xây dựng chương trình thống kê danh sách điểm. Khi học về hàm, hãy tách chương trình thành nhiều phần nhỏ để mã nguồn dễ đọc, dễ kiểm thử và dễ bảo trì hơn.

Trong quá trình học, bạn sẽ gặp lỗi. Đây là một phần bình thường của việc lập trình. Thay vì xóa toàn bộ mã nguồn và làm lại, hãy đọc kỹ thông báo lỗi, xác định dòng gây lỗi, kiểm tra dữ liệu đầu vào và thử sửa từng vấn đề nhỏ. Việc học cách phân tích lỗi quan trọng không kém việc học cú pháp.

Cuối mỗi tuần, bạn nên dành thời gian ôn tập, đánh giá tiến độ và điều chỉnh kế hoạch. Hãy tự trả lời ba câu hỏi. Tuần này mình đã học được gì? Phần nào mình vẫn chưa hiểu? Tuần sau mình cần ưu tiên nội dung nào? Nếu chưa hoàn thành đúng dự kiến, không nên cố học quá nhiều trong một ngày. Thay vào đó, hãy tìm nguyên nhân và sắp xếp lại khối lượng học tập cho phù hợp.

Cuối cùng, sự duy trì đều đặn quan trọng hơn việc học thật nhiều trong một khoảng thời gian ngắn. Chỉ cần học tập trung mỗi ngày, thực hành thường xuyên và hoàn thành từng mục tiêu nhỏ, bạn sẽ tạo được nền tảng vững chắc để tiếp tục học những nội dung nâng cao hơn.
""".strip()


def safe_filename(name: str) -> str:
    for char in '<>:"/\\|?*':
        name = name.replace(char, "-")
    return name.strip()


def generate_voice(voice: str) -> Path:
    payload = {
        "input": LESSON_TEXT,
        "voice": voice,
        "response_format": "wav",
        "speed": 1.0,
    }
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json; charset=utf-8",
    }
    response = requests.post(API_URL, headers=headers, json=payload, timeout=600)
    if response.status_code != 200:
        raise RuntimeError(f"HTTP {response.status_code}: {response.text}")

    output_file = OUTPUT_DIR / f"{safe_filename(voice)}.wav"
    output_file.write_bytes(response.content)
    return output_file


def main() -> int:
    if API_KEY == "YOUR_API_KEY":
        print(
            "Chưa cấu hình API key.\n"
            "PowerShell: $env:TTS_API_KEY=\"API_KEY_CUA_BAN\"\n"
            "Linux/macOS: export TTS_API_KEY=\"API_KEY_CUA_BAN\"",
            file=sys.stderr,
        )
        return 1

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"API: {API_URL}")
    print(f"Thư mục kết quả: {OUTPUT_DIR.resolve()}")
    print(f"Số giọng cần tạo: {len(VOICES)}\n")

    success = 0
    failed = 0

    for index, voice in enumerate(VOICES, start=1):
        print(f"[{index}/{len(VOICES)}] Đang tạo giọng: {voice}")
        try:
            output_file = generate_voice(voice)
            print(f"  Đã lưu: {output_file}")
            success += 1
        except Exception as exc:
            print(f"  Lỗi: {exc}", file=sys.stderr)
            failed += 1

    print(f"\nHoàn thành. Thành công: {success}; Thất bại: {failed}")
    return 0 if failed == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
