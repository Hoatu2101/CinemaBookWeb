from datetime import time, timedelta
from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError

from CinemaBook.models import Cinema, Room, Status, Movie, Showtime
from CinemaBook.validate import validate_showtime, validate_showtime_deletion, check_showtime_has_sold_seats


class AdminDataValidationTestCase(TestCase):
    def setUp(self):
        self.status_ok = Status.objects.create(name="Available")
        self.cinema = Cinema.objects.create(name="Rạp CGV", location="HCM")
        self.room = Room.objects.create(name="Phòng 2", capacity=50, cinema=self.cinema, status=self.status_ok)
        self.movie = Movie.objects.create(movie_name="Phim Độc Lập", duration=90)

    def test_showtime_validation_start_after_end(self):
        """Kiểm tra validator khi Admin nhập suất chiếu có thời gian bắt đầu >= kết thúc"""
        invalid_showtime = Showtime(
            movie=self.movie,
            room=self.room,
            show_date=timezone.now().date() + timedelta(days=1),
            start_time=time(20, 0),
            end_time=time(18, 0)
        )
        with self.assertRaises(ValidationError):
            validate_showtime(invalid_showtime)

    def test_delete_showtime_without_sold_seats_success(self):
        """Suất chiếu chưa có vé/ghế đã đặt được phép xóa bình thường"""
        showtime = Showtime.objects.create(
            movie=self.movie,
            room=self.room,
            show_date=timezone.now().date() + timedelta(days=2),
            start_time=time(10, 0),
            end_time=time(12, 0)
        )
        self.assertFalse(check_showtime_has_sold_seats(showtime))
        showtime_id = showtime.id
        showtime.delete()
        self.assertFalse(Showtime.objects.filter(id=showtime_id).exists())

    def test_delete_showtime_with_sold_seats_raises_validation_error(self):
        """Suất chiếu đã có ít nhất 1 ghế được bán/đặt vé không được phép xóa"""
        from django.contrib.auth.models import User
        from CinemaBook.models import Seat, Booking, Ticket

        user = User.objects.create_user(username="testbuyer", password="password123")
        seat = Seat.objects.create(seat_number="C1", room=self.room)
        showtime = Showtime.objects.create(
            movie=self.movie,
            room=self.room,
            show_date=timezone.now().date() + timedelta(days=3),
            start_time=time(14, 0),
            end_time=time(16, 0)
        )

        booking = Booking.objects.create(
            user=user,
            showtime=showtime,
            total_price=100000.0,
            payment_status='PAID'
        )
        Ticket.objects.create(
            booking=booking,
            seat=seat,
            price=100000.0
        )

        self.assertTrue(check_showtime_has_sold_seats(showtime))
        with self.assertRaises(ValidationError):
            validate_showtime_deletion(showtime)
        with self.assertRaises(ValidationError):
            showtime.delete()
