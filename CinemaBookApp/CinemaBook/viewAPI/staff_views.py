from datetime import datetime
import json
from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_exempt

from ..models import Ticket, UserRole, Cinema, UserProfile


def is_staff_member(user):
    """Kiểm tra người dùng có đúng là Nhân viên rạp (ROLE_STAFF) hay không (Admin không được soát vé)"""
    if not user or not user.is_authenticated:
        return False
    # Admin/Superuser không được phép soát vé
    if user.is_superuser or (hasattr(user, 'profile') and user.profile.role == UserRole.ADMIN):
        return False
    return bool(hasattr(user, 'profile') and user.profile.role == UserRole.STAFF) or (user.is_staff and not user.is_superuser)


@staff_member_required
def staff_check_ticket_view(request):
    """Giao diện Soát vé Camera dành riêng cho Nhân viên rạp (ROLE_STAFF)"""
    user = request.user
    if user.is_superuser or (hasattr(user, 'profile') and user.profile.role == UserRole.ADMIN):
        return render(request, 'admin/check_ticket_scanner.html', {
            'error_message': '⛔ QUYỀN TRUY CẬP BỊ TỪ CHỐI! Quản trị viên hệ thống (Admin) không được phép thực hiện soát vé. Chức năng này chỉ dành cho Nhân viên rạp (ROLE_STAFF).'
        })
    return render(request, 'admin/check_ticket_scanner.html')


@staff_member_required
def staff_register_view(request):
    """Giao diện Viewsite Đăng ký tài khoản Nhân viên Rạp (Role: STAFF)"""
    user = request.user
    
    # Kiểm tra quyền: Superuser, Admin hoặc Cinema Manager
    is_admin = user.is_superuser or (hasattr(user, 'profile') and user.profile.role in [UserRole.ADMIN, UserRole.CINEMA_MANAGER])
    if not is_admin:
        return render(request, 'admin/check_ticket_scanner.html', {
            'error_message': 'Quyền truy cập bị từ chối. Chỉ Quản trị viên mới có quyền đăng ký nhân viên!'
        })

    user_cinema = getattr(user.profile, 'cinema', None) if hasattr(user, 'profile') else None
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        number_phone = request.POST.get('number_phone', '').strip()
        cinema_id = request.POST.get('cinema_id')

        # Validation
        if not username or not password or not name:
            messages.error(request, "Vui lòng điền đầy đủ Tên đăng nhập, Mật khẩu và Họ tên nhân viên!")
        elif password != confirm_password:
            messages.error(request, "Mật khẩu và Xác nhận mật khẩu không khớp nhau!")
        elif User.objects.filter(username=username).exists():
            messages.error(request, f"Tên đăng nhập '{username}' đã tồn tại trên hệ thống!")
        else:
            try:
                # Tìm rạp phụ trách
                target_cinema = None
                if cinema_id and cinema_id.isdigit():
                    target_cinema = Cinema.objects.filter(pk=int(cinema_id)).first()
                elif user_cinema:
                    target_cinema = user_cinema

                if not email:
                    email = f"{username}@cinebook.vn"

                # Tạo User Django (is_staff=True để đăng nhập viewsite/admin & soát vé)
                new_user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=name,
                    is_staff=True,
                    is_superuser=False
                )

                # Tạo/Cập nhật UserProfile gán role STAFF
                profile, _ = UserProfile.objects.get_or_create(user=new_user)
                profile.role = UserRole.STAFF
                profile.name = name
                profile.number_phone = number_phone
                profile.cinema = target_cinema
                profile.save()

                cinema_label = target_cinema.name if target_cinema else "Tất cả rạp"
                messages.success(request, f"🎉 Đã đăng ký thành công Nhân viên: {name} (@{username}) thuộc rạp '{cinema_label}'!")
            except Exception as e:
                messages.error(request, f"Lỗi khi tạo tài khoản nhân viên: {str(e)}")

    # Lấy danh sách rạp khả dụng
    if user.is_superuser or (hasattr(user, 'profile') and user.profile.role == UserRole.ADMIN):
        available_cinemas = Cinema.objects.all()
    else:
        available_cinemas = Cinema.objects.filter(id=user_cinema.id) if user_cinema else Cinema.objects.all()

    # Danh sách nhân viên rạp hiện tại
    staff_profiles = UserProfile.objects.filter(role=UserRole.STAFF).select_related('user', 'cinema').order_by('-user__date_joined')[:20]

    context = {
        'title': 'Đăng Ký Tài Khoản Nhân Viên Rạp (ROLE_STAFF)',
        'available_cinemas': available_cinemas,
        'user_cinema': user_cinema,
        'staff_profiles': staff_profiles,
    }
    return render(request, 'admin/staff_register_form.html', context)


@csrf_exempt
def staff_verify_ticket_api(request):
    """API xác thực và thực hiện Soát vé từ mã QR Code / Mã vé"""
    if not (request.user and request.user.is_authenticated):
        return JsonResponse({'success': False, 'message': 'Bạn cần đăng nhập để thực hiện soát vé!'}, status=401)

    if not is_staff_member(request.user):
        return JsonResponse({'success': False, 'message': 'Quyền truy cập bị từ chối. Chỉ nhân viên mới có quyền soát vé!'}, status=403)

    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Phương thức không hợp lệ!'}, status=405)

    try:
        data = json.loads(request.body)
        ticket_code = (data.get('ticket_code') or '').strip()
    except Exception:
        ticket_code = (request.POST.get('ticket_code') or '').strip()

    if not ticket_code:
        return JsonResponse({'success': False, 'message': 'Vui lòng quét hoặc nhập Mã vé!'}, status=400)

    try:
        ticket = Ticket.objects.select_related(
            'booking', 'booking__user', 'booking__showtime', 'booking__showtime__movie',
            'seat', 'seat__room', 'seat__room__cinema', 'type_ticket'
        ).get(ticket_code__iexact=ticket_code)
    except Ticket.DoesNotExist:
        ticket = Ticket.objects.filter(pk=int(ticket_code)).first() if ticket_code.isdigit() else None

    if not ticket:
        return JsonResponse({'success': False, 'message': f' Không tìm thấy vé với mã "{ticket_code}" trên hệ thống!'}, status=404)

    movie_name, showtime_str, poster_url = "Chưa cập nhật", "Chưa cập nhật", None
    if ticket.booking and ticket.booking.showtime:
        st = ticket.booking.showtime
        if st.movie:
            movie_name = st.movie.movie_name
            poster_url = st.movie.poster.url if st.movie.poster else None
        if st.show_date and st.start_time:
            showtime_str = f"{st.start_time.strftime('%H:%M')} ({st.show_date.strftime('%d/%m/%Y')})"

    room_name = ticket.seat.room.name if (ticket.seat and ticket.seat.room) else "Chưa phân phòng"
    cinema_name = ticket.seat.room.cinema.name if (ticket.seat and ticket.seat.room and ticket.seat.room.cinema) else "Chưa phân rạp"

    ticket_data = {
        'ticket_code': ticket.ticket_code or f"ID #{ticket.id}",
        'movie_name': movie_name,
        'showtime_str': showtime_str,
        'poster_url': poster_url,
        'user_name': ticket.booking.user.username if (ticket.booking and ticket.booking.user) else 'Khách hàng',
        'seat_number': ticket.seat.seat_number if ticket.seat else '-',
        'type_ticket': ticket.type_ticket.name if ticket.type_ticket else 'Vé tiêu chuẩn',
        'room_name': room_name,
        'cinema_name': cinema_name,
        'price': f"{ticket.price:,.0f} VNĐ",
        'used_at': ticket.used_at.strftime('%H:%M:%S - %d/%m/%Y') if ticket.used_at else 'Chưa soát'
    }

    if not request.user.is_superuser and hasattr(request.user, 'profile') and request.user.profile.cinema:
        user_cinema = request.user.profile.cinema
        ticket_cinema = ticket.seat.room.cinema if (ticket.seat and ticket.seat.room and ticket.seat.room.cinema) else None
        if ticket_cinema and ticket_cinema.id != user_cinema.id:
            return JsonResponse({
                'success': False,
                'status_type': 'WRONG_CINEMA',
                'message': f'❌ VÉ NÀY THUỘC RẠP KHÁC ({ticket_cinema.name})! Không thể soát vé tại rạp "{user_cinema.name}".',
                'ticket_info': ticket_data
            }, status=400)

    # Ràng buộc 1: Kiểm tra đơn hàng đã thanh toán chưa
    if ticket.booking and ticket.booking.payment_status != 'PAID':
        return JsonResponse({
            'success': False,
            'status_type': 'UNPAID',
            'message': f'❌ VÉ KHÔNG HỢP LỆ DO CHƯA THANH TOÁN! (Trạng thái: {ticket.booking.payment_status}).',
            'ticket_info': ticket_data
        }, status=400)

    # Ràng buộc 2: Kiểm tra Suất chiếu của vé đã kết thúc hoặc chưa tới ngày chiếu hay chưa
    if ticket.booking and ticket.booking.showtime:
        st = ticket.booking.showtime
        now_dt = timezone.now()

        if st.show_date and st.end_time:
            end_dt_naive = datetime.combine(st.show_date, st.end_time)
            try:
                end_dt = timezone.make_aware(end_dt_naive, timezone.get_current_timezone())
            except Exception:
                end_dt = end_dt_naive

            cmp_now = now_dt if timezone.is_aware(end_dt) else datetime.now()
            if cmp_now > end_dt:
                end_str = st.end_time.strftime('%H:%M')
                date_str = st.show_date.strftime('%d/%m/%Y')
                return JsonResponse({
                    'success': False,
                    'status_type': 'EXPIRED_SHOWTIME',
                    'message': f'❌ MÃ VÉ KHÔNG HỢP LỆ DO SUẤT CHIẾU ĐÃ KẾT THÚC! (Hết hạn lúc {end_str} ngày {date_str}).',
                    'ticket_info': ticket_data
                }, status=400)

        if st.show_date and timezone.localtime(now_dt).date() < st.show_date:
            date_str = st.show_date.strftime('%d/%m/%Y')
            return JsonResponse({
                'success': False,
                'status_type': 'FUTURE_SHOWTIME',
                'message': f'❌ MÃ VÉ CHƯA ĐẾN NGÀY CHIẾU! (Suất chiếu diễn ra vào ngày {date_str}).',
                'ticket_info': ticket_data
            }, status=400)

    if ticket.is_used:
        used_time = ticket.used_at.strftime('%H:%M:%S - %d/%m/%Y') if ticket.used_at else 'Trước đó'
        return JsonResponse({
            'success': False,
            'status_type': 'ALREADY_USED',
            'message': f' VÉ NÀY ĐÃ ĐƯỢC SOÁT VÀO LÚC: {used_time}!',
            'ticket_info': ticket_data
        }, status=400)

    ticket.is_used = True
    ticket.used_at = timezone.now()
    ticket.save()

    ticket_data['used_at'] = ticket.used_at.strftime('%H:%M:%S - %d/%m/%Y')

    return JsonResponse({
        'success': True,
        'status_type': 'SUCCESS',
        'message': 'VÉ HỢP LỆ! SOÁT VÉ THÀNH CÔNG ',
        'ticket_info': ticket_data
    })
