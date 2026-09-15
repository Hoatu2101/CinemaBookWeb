from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.utils import timezone

from .models import Showtime


def validate_showtime(obj):
    if obj.start_time and obj.end_time and obj.start_time >= obj.end_time:
        raise ValidationError(
            "Thời gian bắt đầu phải nhỏ hơn thời gian kết thúc."
        )

    if obj.show_date and obj.show_date < timezone.now().date():
        raise ValidationError(
            "Ngày chiếu phải là ngày hiện tại hoặc trong tương lai."
        )

    try:
        room = obj.room if getattr(obj, 'room_id', None) else None
    except ObjectDoesNotExist:
        room = None

    try:
        movie = obj.movie if getattr(obj, 'movie_id', None) else None
    except ObjectDoesNotExist:
        movie = None

    # 1. Ràng buộc & Tự động tính thời lượng suất chiếu khớp với thời lượng phim (movie.duration)
    if movie and movie.duration and obj.start_time:
        import datetime
        dummy_date = datetime.date(2000, 1, 1)
        dt_start = datetime.datetime.combine(dummy_date, obj.start_time)

        if not obj.end_time:
            dt_end = dt_start + datetime.timedelta(minutes=movie.duration)
            obj.end_time = dt_end.time()
        else:
            dt_end = datetime.datetime.combine(dummy_date, obj.end_time)
            if dt_end <= dt_start:
                dt_end += datetime.timedelta(days=1)
            actual_duration = int((dt_end - dt_start).total_seconds() / 60)
            if actual_duration != movie.duration:
                raise ValidationError(
                    f"Độ dài suất chiếu ({actual_duration} phút) phải khớp với đúng thời lượng của bộ phim '{movie.movie_name}' ({movie.duration} phút)."
                )

    if room and obj.show_date and obj.start_time and obj.end_time:
        overlapping_showtimes = Showtime.objects.filter(
            room=room,
            show_date=obj.show_date,
            start_time__lt=obj.end_time,
            end_time__gt=obj.start_time
        )
        if obj.pk:
            overlapping_showtimes = overlapping_showtimes.exclude(pk=obj.pk)

        if overlapping_showtimes.exists():
            raise ValidationError(
                "Suất chiếu này trùng với một suất chiếu khác trong cùng phòng và ngày."
            )

    if room and room.status and room.status.name not in ["Available", "Hoạt động", "Đang hoạt động"]:
        raise ValidationError(
            "Phòng chiếu hiện không khả dụng. Vui lòng chọn phòng khác."
        )


def check_showtime_has_sold_seats(obj):
    """
    Kiểm tra xem suất chiếu đã có ít nhất 1 ghế được bán/đặt vé hay chưa.
    Trả về True nếu đã có ghế bán vé, ngược lại False.
    """
    from .models import Ticket, SeatShowtimeStatus, SeatStatus
    if not obj or not obj.pk:
        return False

    if Ticket.objects.filter(booking__showtime=obj).exists():
        return True
    if SeatShowtimeStatus.objects.filter(showtime=obj, status=SeatStatus.BOOKED).exists():
        return True
    if hasattr(obj, 'bookings') and obj.bookings.filter(payment_status__in=['PAID', 'COMPLETED']).exists():
        return True
    return False


def validate_showtime_deletion(obj):
    """
    Ràng buộc không được xóa suất chiếu nếu đã có ít nhất 1 ghế được bán/đặt vé.
    """
    if check_showtime_has_sold_seats(obj):
        raise ValidationError(
            "Không thể xóa suất chiếu này vì đã có ghế được đặt/bán vé!"
        )



def validate_seat(obj):
    from .models import Seat

    if obj.room and obj.seat_number:
        
        duplicate_seats = Seat.objects.filter(
            room=obj.room,
            seat_number=obj.seat_number
        )
        if obj.pk:
            duplicate_seats = duplicate_seats.exclude(pk=obj.pk)

        if duplicate_seats.exists():
            raise ValidationError(
                f"Mã ghế '{obj.seat_number}' đã tồn tại trong phòng '{obj.room.name}'."
            )

        if obj.room.capacity is not None:
            existing_seats = Seat.objects.filter(room=obj.room)
            if obj.pk:
                existing_seats = existing_seats.exclude(pk=obj.pk)

            if existing_seats.count() + 1 > obj.room.capacity:
                raise ValidationError(
                    f"Số lượng ghế không được vượt quá sức chứa tối đa của phòng '{obj.room.name}' ({obj.room.capacity} ghế)."
                )


def validate_room(obj):
    if obj.capacity is not None and obj.capacity < 0:
        raise ValidationError(
            "Sức chứa của phòng chiếu không được là số âm."
        )

    if obj.pk:
        existing_seats_count = obj.seats.count()
        if obj.capacity is not None and obj.capacity < existing_seats_count:
            raise ValidationError(
                f"Sức chứa của phòng ({obj.capacity} ghế) không được nhỏ hơn số lượng ghế hiện tại trong phòng ({existing_seats_count} ghế)."
            )
