from datetime import time, timedelta
from django.core import mail
from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from CinemaBook.models import Cinema, Room, Status, Movie, Showtime, Booking, Ticket, Seat
from CinemaBook.Service.email_service import send_ticket_confirmation_email


class EmailNotificationTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(
            username='testcustomer',
            email='customer@example.com',
            password='password123',
            first_name='Nguyễn Văn Test'
        )

        self.status_ok = Status.objects.create(name="Available")
        self.cinema = Cinema.objects.create(name="Rạp CineBook Hùng Vương", location="TP.HCM")
        self.room = Room.objects.create(name="Phòng 01", capacity=100, cinema=self.cinema, status=self.status_ok)
        self.seat = Seat.objects.create(seat_number="C05", room=self.room)

        self.movie = Movie.objects.create(movie_name="Avatar: The Way of Water", duration=190)
        self.showtime = Showtime.objects.create(
            movie=self.movie,
            room=self.room,
            show_date=timezone.now().date() + timedelta(days=1),
            start_time=time(19, 30),
            end_time=time(22, 40)
        )

        self.booking = Booking.objects.create(
            user=self.user,
            showtime=self.showtime,
            total_price=120000.0,
            payment_status='PAID',
            payment_method='VNPAY'
        )
        self.ticket = Ticket.objects.create(
            booking=self.booking,
            seat=self.seat,
            price=120000.0,
            ticket_code="TICKET_EMAIL_TEST_99",
            is_used=False
        )

    def test_send_ticket_confirmation_email_success(self):
        """Kiểm tra hàm send_ticket_confirmation_email gửi mail thành công đến đúng recipient và chứa đúng nội dung vé"""
        mail.outbox = []
        result = send_ticket_confirmation_email(self.booking)

        self.assertTrue(result)
        self.assertEqual(len(mail.outbox), 1)

        sent_email = mail.outbox[0]
        self.assertIn('customer@example.com', sent_email.to)
        self.assertIn(f"#{self.booking.id}", sent_email.subject)
        self.assertIn("Avatar: The Way of Water", sent_email.body)
        self.assertIn("C05", sent_email.body)
        self.assertIn("TICKET_EMAIL_TEST_99", sent_email.body)

        # Kiểm tra nội dung HTML có chứa đường dẫn tạo mã QR Code
        html_alt = sent_email.alternatives[0][0]
        self.assertIn("create-qr-code", html_alt)
        self.assertIn("TICKET_EMAIL_TEST_99", html_alt)
