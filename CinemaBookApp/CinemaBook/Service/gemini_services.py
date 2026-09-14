import os
from django.conf import settings

try:
    from google import genai
except ImportError:
    genai = None

def get_gemini_client():
    if genai is None:
        raise ValueError("Thư viện google-genai chưa được cài đặt!")
    api_key = getattr(settings, 'GEMINI_API_KEY', None) or os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("Chưa tìm thấy GEMINI_API_KEY! Vui lòng cấu hình GEMINI_API_KEY trong file .env hoặc settings.py.")
    return genai.Client(api_key=api_key)

def ask_gemini(prompt):
    client = get_gemini_client()
    preferred_models = [
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-1.5-flash",
        "gemini-1.5-flash-latest",
        "gemini-1.5-pro",
        "gemini-2.0-flash-lite",
    ]
    last_error = None

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

    # Dynamic fallback: query available models for this specific API key
    try:
        for model_info in client.models.list():
            m_name = getattr(model_info, 'name', '') or str(model_info)
            if 'gemini' in m_name.lower():
                try:
                    response = client.models.generate_content(
                        model=m_name,
                        contents=prompt
                    )
                    if response and response.text:
                        return response.text
                except Exception as inner_e:
                    last_error = inner_e
    except Exception:
        pass

    if last_error:
        raise last_error

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
