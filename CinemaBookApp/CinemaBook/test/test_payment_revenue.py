from datetime import time, timedelta
from unittest.mock import patch
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from CinemaBook.models import (
    Cinema, Room, Status, Movie, Showtime, Seat, Booking, Ticket, SeatShowtimeStatus, SeatStatus, UserProfile, UserRole
)


class PaymentAndRevenueTestCase(APITestCase):
    def setUp(self):
        super().setUp()
        self.client = APIClient()

        self.user = User.objects.create_user(username='payuser', password='password123')
        self.admin_user = User.objects.create_superuser(username='adminpay', email='admin@test.com', password='password123')
        UserProfile.objects.get_or_create(user=self.admin_user, defaults={'role': UserRole.ADMIN})

        self.status_ok = Status.objects.create(name="Active")
        self.cinema = Cinema.objects.create(name="Rạp Lotte Westlake", location="Hà Nội")
        self.room = Room.objects.create(name="Phòng 5", capacity=60, cinema=self.cinema, status=self.status_ok)
        self.seat = Seat.objects.create(seat_number="D1", room=self.room)

        self.movie = Movie.objects.create(movie_name="Oppenheimer", duration=180)
        self.showtime = Showtime.objects.create(
            movie=self.movie,
            room=self.room,
            show_date=timezone.now().date() + timedelta(days=1),
            start_time=time(19, 0),
            end_time=time(22, 0)
        )

        self.booking = Booking.objects.create(
            user=self.user,
            showtime=self.showtime,
            total_price=120000.0,
            payment_status='PENDING',
            payment_method='VNPAY'
        )
        self.ticket = Ticket.objects.create(
            booking=self.booking,
            seat=self.seat,
            price=120000.0
        )

        self.vnpay_return_url = reverse('vnpay_return')

    @patch('CinemaBook.viewAPI.payment_views.VNPayService.validate_response')
    def test_vnpay_return_success(self, mock_validate):
        """Test VNPay Return URL callback thanh toán thành công ('00') -> Cập nhật PAID & 302 Redirect"""
        mock_validate.return_value = True

        params = {
            'vnp_TxnRef': str(self.booking.id),
            'vnp_ResponseCode': '00',
            'vnp_SecureHash': 'valid_hash'
        }
        response = self.client.get(self.vnpay_return_url, params)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertIn('status=success', response['Location'])

        self.booking.refresh_from_db()
        self.assertEqual(self.booking.payment_status, 'PAID')

        sss = SeatShowtimeStatus.objects.filter(showtime=self.showtime, seat=self.seat).first()
        self.assertIsNotNone(sss)
        self.assertEqual(sss.status, SeatStatus.BOOKED)

    @patch('CinemaBook.viewAPI.payment_views.VNPayService.validate_response')
    def test_vnpay_return_failed_response_code(self, mock_validate):
        """Test VNPay Return URL callback thanh toán thất bại ('99') -> 302 Redirect thất bại"""
        mock_validate.return_value = True

        params = {
            'vnp_TxnRef': str(self.booking.id),
            'vnp_ResponseCode': '99',
            'vnp_SecureHash': 'hash'
        }
        response = self.client.get(self.vnpay_return_url, params)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertIn('status=failed', response['Location'])

        self.booking.refresh_from_db()
        self.assertEqual(self.booking.payment_status, 'PENDING')
