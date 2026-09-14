import json
import calendar
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Sum
from django.utils import timezone
from django.contrib.admin.views.decorators import staff_member_required

from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions

from ..models import Booking, Movie, SeatShowtimeStatus, Cinema, SeatStatus, UserRole
from ..Service.VNpayservices import VNPayService
from ..Service.email_service import send_ticket_confirmation_email


def index(request):
    return HttpResponse("Welcome to CinemaBook!")


@staff_member_required
def revenue_stats_view(request):
    now = timezone.now()
    p = request.GET

    period = p.get('period', 'day')
    if period not in ['day', 'month', 'quarter', 'year']:
        period = 'day'

    try:
        selected_year = int(p.get('year', now.year))
    except (ValueError, TypeError):
        selected_year = now.year

    try:
        selected_month = int(p.get('month', now.month))
    except (ValueError, TypeError):
        selected_month = now.month
    if not (1 <= selected_month <= 12):
        selected_month = now.month

    selected_movie_id = int(p.get('movie_id')) if p.get('movie_id', '').isdigit() else None
    selected_cinema_id = int(p.get('cinema_id')) if p.get('cinema_id', '').isdigit() else None

    # Phân quyền: Super Admin vs Admin Rạp
    is_super_admin = request.user.is_superuser or (
        hasattr(request.user, 'profile') and request.user.profile.role == UserRole.ADMIN
    )

    user_cinema = None
    if not is_super_admin:
        if hasattr(request.user, 'profile') and request.user.profile.cinema:
            user_cinema = request.user.profile.cinema
            selected_cinema_id = user_cinema.id
        else:
            selected_cinema_id = None

    base_qs = Booking.objects.all()
    if not is_super_admin:
        base_qs = base_qs.filter(showtime__room__cinema=user_cinema) if user_cinema else base_qs.none()
    elif selected_cinema_id:
        base_qs = base_qs.filter(showtime__room__cinema_id=selected_cinema_id)

    if selected_movie_id:
        base_qs = base_qs.filter(showtime__movie_id=selected_movie_id)

    # Key Metrics
    calc_sum = lambda qs: qs.aggregate(s=Sum('total_price'))['s'] or 0.0
    today_revenue = calc_sum(base_qs.filter(created_at__date=now.date()))
    this_month_revenue = calc_sum(base_qs.filter(created_at__year=now.year, created_at__month=now.month))

    curr_q = (now.month - 1) // 3 + 1
    q_months = [(curr_q - 1) * 3 + i for i in (1, 2, 3)]
    this_quarter_revenue = calc_sum(base_qs.filter(created_at__year=now.year, created_at__month__in=q_months))

    this_year_revenue = calc_sum(base_qs.filter(created_at__year=now.year))
    overall_revenue = calc_sum(base_qs)

    years_qs = Booking.objects.dates('created_at', 'year')
    available_years = sorted(list({d.year for d in years_qs} | {now.year}), reverse=True)
    movies = Movie.objects.all()
    all_cinemas = Cinema.objects.all() if is_super_admin else ([user_cinema] if user_cinema else [])

    table_rows, chart_labels, chart_data = [], [], []

    if period == 'day':
        _, days_in_month = calendar.monthrange(selected_year, selected_month)
        qs = base_qs.filter(created_at__year=selected_year, created_at__month=selected_month)
        for day in range(1, days_in_month + 1):
            day_qs = qs.filter(created_at__day=day)
            rev, cnt = calc_sum(day_qs), day_qs.count()
            lbl = f"{day:02d}/{selected_month:02d}"
            chart_labels.append(lbl)
            chart_data.append(rev)
            if cnt > 0 or rev > 0:
                table_rows.append({'label': lbl, 'count': cnt, 'revenue': rev})

    elif period == 'month':
        qs = base_qs.filter(created_at__year=selected_year)
        for m in range(1, 13):
            m_qs = qs.filter(created_at__month=m)
            rev, cnt = calc_sum(m_qs), m_qs.count()
            lbl = f"Tháng {m}"
            chart_labels.append(lbl)
            chart_data.append(rev)
            if cnt > 0 or rev > 0:
                table_rows.append({'label': lbl, 'count': cnt, 'revenue': rev})

    elif period == 'quarter':
        qs = base_qs.filter(created_at__year=selected_year)
        for q in range(1, 5):
            qm = [(q - 1) * 3 + i for i in (1, 2, 3)]
            q_qs = qs.filter(created_at__month__in=qm)
            rev, cnt = calc_sum(q_qs), q_qs.count()
            lbl = f"Quý {q}"
            chart_labels.append(lbl)
            chart_data.append(rev)
            if cnt > 0 or rev > 0:
                table_rows.append({'label': lbl, 'count': cnt, 'revenue': rev})

    elif period == 'year':
        for y in sorted(available_years):
            y_qs = base_qs.filter(created_at__year=y)
            rev, cnt = calc_sum(y_qs), y_qs.count()
            lbl = f"Năm {y}"
            chart_labels.append(lbl)
            chart_data.append(rev)
            if cnt > 0 or rev > 0:
                table_rows.append({'label': lbl, 'count': cnt, 'revenue': rev})

    top_movies_qs = base_qs.values('showtime__movie__movie_name').annotate(
        total_rev=Sum('total_price')
    ).order_by('-total_rev')[:5]

    top_movie_labels = [item['showtime__movie__movie_name'] or 'Phim chưa xác định' for item in top_movies_qs]
    top_movie_data = [float(item['total_rev'] or 0) for item in top_movies_qs]

    context = {
        'period': period,
        'selected_year': selected_year,
        'selected_month': selected_month,
        'selected_movie_id': selected_movie_id,
        'selected_cinema_id': selected_cinema_id,
        'user_cinema': user_cinema,
        'is_super_admin': is_super_admin,
        'all_cinemas': all_cinemas,
        'available_years': available_years,
        'available_months': list(range(1, 13)),
        'movies': movies,
        'today_revenue': today_revenue,
        'this_month_revenue': this_month_revenue,
        'this_quarter_revenue': this_quarter_revenue,
        'this_year_revenue': this_year_revenue,
        'overall_revenue': overall_revenue,
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
        'top_movie_labels': json.dumps(top_movie_labels),
        'top_movie_data': json.dumps(top_movie_data),
        'table_rows': table_rows,
        'title': f"Thống kê doanh thu {'- ' + user_cinema.name if user_cinema else ''}",
    }
    return render(request, 'admin/revenue_stats.html', context)


@api_view(['GET', 'POST'])
@permission_classes([permissions.AllowAny])
def vnpay_return_view(request):
    """Callback IPN / Return URL từ VNPay Portal về hệ thống sau khi thanh toán"""
    params = request.GET.dict() if request.method == 'GET' else request.data.dict()
    vnpay_service = VNPayService()
    is_valid = vnpay_service.validate_response(params)
    
    raw_order_id = params.get('vnp_TxnRef', '').strip()
    order_id = raw_order_id.split('_')[0] if '_' in raw_order_id else raw_order_id
    response_code = params.get('vnp_ResponseCode')

    booking = None
    showtime_id, seat_ids = "", []
    try:
        if order_id and order_id.isdigit():
            booking = Booking.objects.get(pk=int(order_id))
            showtime_id = str(booking.showtime_id)
            seat_ids = [str(t.seat_id) for t in booking.tickets.all()]
    except (Booking.DoesNotExist, ValueError):
        pass

    if is_valid and response_code == '00':
        if booking:
            booking.payment_status = 'PAID'
            booking.payment_method = 'VNPAY'
            booking.save()

            for t in booking.tickets.all():
                SeatShowtimeStatus.objects.update_or_create(
                    showtime=booking.showtime, seat=t.seat,
                    defaults={'status': SeatStatus.BOOKED, 'user': booking.user}
                )

            # Gửi email xác nhận đặt vé cho khách hàng
            send_ticket_confirmation_email(booking)

        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3001')
        return HttpResponseRedirect(f"{frontend_url}/vnpay-return?status=success&booking_id={order_id}&showtime_id={showtime_id}&seat_ids={','.join(seat_ids)}")

    frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3001')
    return HttpResponseRedirect(f"{frontend_url}/vnpay-return?status=failed&booking_id={order_id}&showtime_id={showtime_id}&seat_ids={','.join(seat_ids)}")
