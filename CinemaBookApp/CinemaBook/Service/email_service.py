import logging
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

logger = logging.getLogger(__name__)


def send_ticket_confirmation_email(booking):
    """
    Gửi email xác nhận đặt vé thành công kèm mã vé cho khách hàng.
    :param booking: Đối tượng Booking (models.Booking)
    :return: True nếu gửi thành công, False nếu không gửi được
    """
    if not booking or not booking.user:
        logger.warning("Không thể gửi email xác nhận vé: Booking hoặc User không hợp lệ.")
        return False

    try:
        booking.user.refresh_from_db()
    except Exception:
        pass

    recipient_email = getattr(booking.user, 'email', '').strip()
    if not recipient_email:
        username = booking.user.username
        recipient_email = username if '@' in username else f"{username}@gmail.com"
        logger.info(f"Người dùng #{booking.user.id} ({booking.user.username}) không có email, tự động dùng {recipient_email}")

    customer_name = getattr(booking.user, 'first_name', '') or booking.user.username
    if hasattr(booking.user, 'profile') and booking.user.profile.name:
        customer_name = booking.user.profile.name

    showtime = booking.showtime
    movie_name = showtime.movie.movie_name if (showtime and showtime.movie) else "N/A"
    cinema_name = showtime.room.cinema.name if (showtime and showtime.room and showtime.room.cinema) else "N/A"
    room_name = showtime.room.name if (showtime and showtime.room) else "N/A"
    
    show_date_str = showtime.show_date.strftime('%d/%m/%Y') if (showtime and showtime.show_date) else "N/A"
    start_time_str = showtime.start_time.strftime('%H:%M') if (showtime and showtime.start_time) else "N/A"
    end_time_str = showtime.end_time.strftime('%H:%M') if (showtime and showtime.end_time) else "N/A"

    tickets = booking.tickets.all()
    seat_list = []
    ticket_codes = []
    tickets_qr_html = ""
    for t in tickets:
        seat_num = t.seat.seat_number if t.seat else f"ID {t.seat_id}"
        seat_list.append(seat_num)
        ticket_codes.append(f"{seat_num}: {t.ticket_code}")
        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=180x180&data={t.ticket_code}"
        tickets_qr_html += f"""
        <div style="background: #ffffff; border: 1px solid #cbd5e1; border-radius: 8px; padding: 14px; margin-top: 12px; text-align: center;">
            <div style="font-size: 15px; font-weight: bold; color: #1e293b; margin-bottom: 8px;">
                🎟️ Ghế: <span style="color: #e50914;">{seat_num}</span>
            </div>
            <div style="margin: 10px 0;">
                <img src="{qr_url}" alt="Mã QR Soát Vé - {t.ticket_code}" width="160" height="160" style="border: 2px solid #e2e8f0; border-radius: 8px; padding: 4px; background: #fff;" />
            </div>
            <div style="font-family: monospace; font-size: 15px; font-weight: bold; color: #2563eb; letter-spacing: 1px;">
                MÃ VÉ: {t.ticket_code}
            </div>
        </div>
        """

    seats_str = ", ".join(seat_list) if seat_list else "N/A"
    ticket_codes_str = "\n".join([f"  - Ghế {code}" for code in ticket_codes]) if ticket_codes else "N/A"
    formatted_price = f"{booking.total_price:,.0f}".replace(",", ".") + " VNĐ" if booking.total_price else "0 VNĐ"

    subject = f"[CineBook] Xác Nhận Đặt Vé Thành Công - Mã Đơn #{booking.id}"
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'CineBook <noreply@cinebook.com>')

    # Plain text version
    text_content = f"""
Xin chào {customer_name},

Cảm ơn bạn đã đặt vé xem phim tại hệ thống CineBook!
Đơn đặt vé #{booking.id} của bạn đã được thanh toán thành công qua {booking.payment_method or 'Online'}.

--- THÔNG TIN VÉ XEM PHIM ---
Mã Đơn Hàng: #{booking.id}
Phim: {movie_name}
Rạp: {cinema_name} ({room_name})
Suất Chiếu: {start_time_str} - {end_time_str} (Ngày {show_date_str})
Danh Sách Ghế: {seats_str}
Tổng Tiền: {formatted_price}

--- MÃ VÉ CỦA BẠN ---
{ticket_codes_str}

Vui lòng đưa mã vé hoặc hình ảnh QR code cho nhân viên soát vé tại rạp để nhận vé vào xem phim.
Chúc bạn có những giây phút xem phim tuyệt vời!

Trân trọng,
Đội ngũ CineBook
"""

    # HTML formatted version
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background-color: #f4f6f9; margin: 0; padding: 20px; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #e50914, #b20710); padding: 24px; text-align: center; color: #ffffff; }}
        .header h1 {{ margin: 0; font-size: 24px; text-transform: uppercase; letter-spacing: 1px; }}
        .content {{ padding: 24px; }}
        .greeting {{ font-size: 16px; margin-bottom: 16px; }}
        .ticket-card {{ background: #fafafa; border: 1px solid #e2e8f0; border-radius: 6px; padding: 18px; margin: 20px 0; }}
        .ticket-title {{ font-size: 18px; font-weight: bold; color: #e50914; margin-bottom: 12px; border-bottom: 2px solid #e50914; padding-bottom: 6px; }}
        .detail-row {{ display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 14px; }}
        .label {{ font-weight: 600; color: #666; }}
        .value {{ font-weight: bold; color: #111; }}
        .tickets-box {{ background: #f8fafc; border: 1px dashed #cbd5e1; padding: 14px; border-radius: 6px; margin-top: 16px; }}
        .footer {{ background: #f1f5f9; padding: 16px; text-align: center; font-size: 12px; color: #64748b; border-top: 1px solid #e2e8f0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>CineBook</h1>
            <p style="margin: 4px 0 0 0; font-size: 14px; opacity: 0.9;">Xác Nhận Đặt Vé Thành Công</p>
        </div>
        <div class="content">
            <div class="greeting">Xin chào <strong>{customer_name}</strong>,</div>
            <p>Cảm ơn bạn đã tin tưởng dịch vụ của CineBook! Đơn vé <strong>#{booking.id}</strong> của bạn đã thanh toán thành công.</p>
            
            <div class="ticket-card">
                <div class="ticket-title">🎬 {movie_name}</div>
                <div class="detail-row"><span class="label">Rạp chiếu:</span> <span class="value">{cinema_name} - {room_name}</span></div>
                <div class="detail-row"><span class="label">Suất chiếu:</span> <span class="value">{start_time_str} - {end_time_str} ({show_date_str})</span></div>
                <div class="detail-row"><span class="label">Ghế đã chọn:</span> <span class="value">{seats_str}</span></div>
                <div class="detail-row"><span class="label">Tổng tiền:</span> <span class="value" style="color: #e50914;">{formatted_price}</span></div>
                
                <div class="tickets-box">
                    <div style="font-size: 14px; font-weight: bold; color: #334155; margin-bottom: 4px; text-align: center;">
                        📱 MÃ QR SOÁT VÉ VÀO RẠP
                    </div>
                    <div style="font-size: 12px; color: #64748b; text-align: center; margin-bottom: 12px;">
                        (Nhân viên sẽ quét mã QR bên dưới khi bạn đến rạp xem phim)
                    </div>
                    {tickets_qr_html}
                </div>
            </div>
            
            <p style="font-size: 13px; color: #64748b; text-align: center;">Vui lòng trình mã QR hoặc mã vé trên cho nhân viên soát vé tại rạp để nhận vé vào xem phim.</p>
        </div>
        <div class="footer">
            © 2026 CineBook System. Mọi thắc mắc vui lòng liên hệ bộ phận hỗ trợ khách hàng.
        </div>
    </div>
</body>
</html>
"""

    try:
        msg = EmailMultiAlternatives(subject, text_content, from_email, [recipient_email])
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)
        logger.info(f"Đã gửi email xác nhận đặt vé #{booking.id} tới {recipient_email}")
        return True
    except Exception as e:
        logger.error(f"Lỗi gửi email xác nhận vé #{booking.id} tới {recipient_email}: {str(e)}")
        return False
