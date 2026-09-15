import os
import json
import urllib.request
import urllib.error
from django.conf import settings

try:
    from google import genai
except ImportError:
    genai = None

try:
    import google.generativeai as legacy_genai
except ImportError:
    legacy_genai = None


def get_api_key():
    api_key = getattr(settings, 'GEMINI_API_KEY', None) or os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("Chưa tìm thấy GEMINI_API_KEY! Vui lòng cấu hình GEMINI_API_KEY trong file .env hoặc settings.py.")
    return api_key


def _ask_gemini_rest_api(api_key, prompt):
    """Fallback gọi trực tiếp REST API của Google Gemini qua urllib (không phụ thuộc SDK)."""
    models = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]
    last_err = None
    for model in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ]
        }
        try:
            req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method='POST')
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                try:
                    text = data['candidates'][0]['content']['parts'][0]['text']
                    if text:
                        return text
                except (KeyError, IndexError):
                    pass
        except urllib.error.HTTPError as he:
            err_body = he.read().decode('utf-8', errors='ignore')
            last_err = Exception(f"Gemini REST Error {he.code}: {err_body}")
        except Exception as e:
            last_err = e
    if last_err:
        raise last_err
    raise ValueError("Không nhận được phản hồi từ Gemini API.")


def ask_gemini(prompt):
    api_key = get_api_key()
    last_error = None

    # Tier 1: Try new google.genai SDK
    if genai is not None:
        try:
            client = genai.Client(api_key=api_key)
            preferred_models = [
                "gemini-2.5-flash",
                "gemini-2.0-flash",
                "gemini-1.5-flash",
                "gemini-1.5-pro",
            ]
            for model_name in preferred_models:
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt
                    )
                    if response and response.text:
                        return response.text
                except Exception as e:
                    last_error = e
        except Exception as e:
            last_error = e

    # Tier 2: Try legacy google.generativeai SDK
    if legacy_genai is not None:
        try:
            legacy_genai.configure(api_key=api_key)
            legacy_models = ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-pro"]
            for m in legacy_models:
                try:
                    mod = legacy_genai.GenerativeModel(m)
                    res = mod.generate_content(prompt)
                    if res and res.text:
                        return res.text
                except Exception as e:
                    last_error = e
        except Exception as e:
            last_error = e

    # Tier 3: Direct HTTP REST Call (Pure Python fallback - guaranteed zero missing dependency)
    try:
        return _ask_gemini_rest_api(api_key, prompt)
    except Exception as rest_err:
        last_error = rest_err

    if last_error:
        raise last_error
    raise ValueError("Không thể kết nối đến Gemini AI.")

def ask_gemini_cinema_system(prompt):
    """Hỏi AI Gemini với ràng buộc BẮT BUỘC chỉ trả lời các câu hỏi liên quan đến hệ thống rạp phim CineBook."""
    system_instruction = (
        "Bạn là Trợ lý Ảo AI chính thức của Hệ thống Rạp chiếu phim CineBook (CinemaBook System).\n"
        "QUY TẮC CỰC KỲ QUAN TRỌNG VÀ BẮT BUỘC:\n"
        "1. Bạn CHỈ ĐƯỢC PHÉP trả lời các câu hỏi liên quan trực tiếp đến hệ thống rạp phim CineBook (bao gồm: thông tin phim, suất chiếu, lịch chiếu, giá vé, cách đặt vé online, thanh toán VNPAY, mã QR soát vé, quy định rạp, đồ ăn bắp nước, loại ghế, đăng ký/đăng nhập tài khoản, lịch sử vé, liên hệ hỗ trợ).\n"
        "2. Nếu câu hỏi của người dùng KHÔNG liên quan đến hệ thống rạp chiếu phim CineBook (ví dụ: giải toán, viết code, thời tiết tổng quan, lịch sử thế giới, game, giải trí chung, tư vấn cá nhân...), bạn BẮT BUỘC phải từ chối lịch sự bằng câu trả lời:\n"
        "'Xin lỗi, tôi là Trợ lý Ảo CineBook và chỉ có thể hỗ trợ các câu hỏi liên quan đến hệ thống rạp chiếu phim (suất chiếu, giá vé, đặt vé, ghế ngồi, thanh toán VNPAY...). Vui lòng đặt câu hỏi liên quan đến rạp phim CineBook!'\n"
        "3. Trả lời ngắn gọn, lịch sự, thân thiện bằng tiếng Việt."
    )
    full_prompt = f"{system_instruction}\n\nCâu hỏi từ khách hàng: {prompt}"
    return ask_gemini(full_prompt)

def generate_movie_description(movie_name, categories="", director="", actor=""):
    prompt = (
        f"Hãy viết một đoạn mô tả/tóm tắt nội dung phim ngắn gọn, lôi cuốn (khoảng 60 - 90 từ) bằng tiếng Việt cho bộ phim:\n"
        f"- Tên phim: {movie_name}\n"
        f"- Thể loại: {categories if categories else 'Chưa rõ'}\n"
        f"- Đạo diễn: {director if director else 'Chưa rõ'}\n"
        f"- Diễn viên: {actor if actor else 'Chưa rõ'}\n\n"
        f"Yêu cầu CỰC KỲ QUAN TRỌNG: Ngắn gọn, cô đọng, kịch tính, không chào hỏi thừa, không dài dòng."
    )
    return ask_gemini(prompt)

def analyze_revenue_data(revenue_summary):
    today = float(revenue_summary.get('today', 0))
    month = float(revenue_summary.get('month', 0))
    quarter = float(revenue_summary.get('quarter', 0))
    year = float(revenue_summary.get('year', 0))
    overall = float(revenue_summary.get('overall', 0))
    period = revenue_summary.get('period', 'Tổng quan')

    prompt = (
        f"Bạn là chuyên gia tài chính rạp phim. Hãy đưa ra bài đánh giá doanh thu CỰC KỲ NGẮN GỌN & CÔ ĐỌNG bằng tiếng Việt dựa trên số liệu:\n"
        f"- Hôm nay: {today:,.0f} VNĐ\n"
        f"- Tháng này: {month:,.0f} VNĐ\n"
        f"- Quý này: {quarter:,.0f} VNĐ\n"
        f"- Năm nay: {year:,.0f} VNĐ\n"
        f"- Tích lũy: {overall:,.0f} VNĐ\n\n"
        f"Yêu cầu trình bày (ngắn gọn, tối đa 4-5 dòng):\n"
        f"Đánh giá nhanh**: [1 câu nhận xét tình hình]\n"
        f"3 Khuyến nghị ngắn**:\n"
        f"• Ý 1 (ngắn gọn 1 câu)\n"
        f"• Ý 2 (ngắn gọn 1 câu)\n"
        f"• Ý 3 (ngắn gọn 1 câu)"
    )
    return ask_gemini(prompt)
