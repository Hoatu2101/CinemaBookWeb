from datetime import time, timedelta
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from CinemaBook.models import (
    UserRole, Cinema, Room, Status, Movie, Showtime, Booking, Ticket, Seat
)


class StaffTicketVerificationTestCase(APITestCase):
    def setUp(self):
        super().setUp()
        self.client = APIClient() 
        self.verify_url = reverse('ticket-verify')

        self.normal_user = User.objects.create_user(
            username='user1', email='user1@test.com', password='password123'
        )

        self.staff_user = User.objects.create_user(
            username='staff1', email='staff1@test.com', password='password123'
        )
        self.staff_user.profile.role = UserRole.STAFF
        self.staff_user.profile.save()

        self.status_ok = Status.objects.create(name="Available")
        self.cinema = Cinema.objects.create(name="Rạp CGV Test", location="Hà Nội")
        self.room = Room.objects.create(name="Phòng 1", capacity=100, cinema=self.cinema, status=self.status_ok)
        self.seat = Seat.objects.create(seat_number="A1", room=self.room)

        self.movie = Movie.objects.create(movie_name="Phim Test Admin", duration=120)
        self.showtime = Showtime.objects.create(
            movie=self.movie,
            room=self.room,
            show_date=timezone.now().date() + timedelta(days=1),
            start_time=time(19, 0),
            end_time=time(21, 0)
        )

        self.booking = Booking.objects.create(
            user=self.normal_user,
            showtime=self.showtime,
            total_price=100000.0,
            payment_status='PAID'
        )
        self.ticket = Ticket.objects.create(
            booking=self.booking,
            seat=self.seat,
            price=100000.0,
            ticket_code="TICKET_TEST_123456",
            is_used=False
        )

    def test_verify_ticket_unauthenticated(self):
        """Khách chưa đăng nhập quét mã vé -> 401 Unauthorized"""
        response = self.client.post(self.verify_url, {'ticket_code': 'TICKET_TEST_123456'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_verify_ticket_forbidden_regular_user(self):
        """Khách hàng thường (role USER) thử quét vé -> 403 Forbidden"""
        getattr(self.client, 'force_authenticate')(user=self.normal_user)
        response = self.client.post(self.verify_url, {'ticket_code': 'TICKET_TEST_123456'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_verify_ticket_empty_code(self):
        """Nhân viên gửi mã vé trống -> 400 Bad Request"""
        getattr(self.client, 'force_authenticate')(user=self.staff_user)
        response = self.client.post(self.verify_url, {'ticket_code': '   '}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        resp_data = getattr(response, 'data', {})
        self.assertIn('error', resp_data)

    def test_verify_ticket_not_found(self):
        """Nhân viên quét mã vé không tồn tại -> 404 Not Found"""
        getattr(self.client, 'force_authenticate')(user=self.staff_user)
        response = self.client.post(self.verify_url, {'ticket_code': 'NON_EXISTENT_CODE'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_verify_ticket_success(self):
        """Nhân viên quét mã vé hợp lệ lần đầu -> 200 OK & vé được đổi trạng thái is_used=True"""
        getattr(self.client, 'force_authenticate')(user=self.staff_user)
        response = self.client.post(self.verify_url, {'ticket_code': 'TICKET_TEST_123456'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        resp_data = getattr(response, 'data', {})
        self.assertTrue(resp_data.get('success'))

        self.ticket.refresh_from_db()
        self.assertTrue(self.ticket.is_used)

    def test_verify_ticket_already_used(self):
        """Nhân viên quét lại mã vé đã được soát -> 400 Bad Request"""
        self.ticket.is_used = True
        self.ticket.save()

        getattr(self.client, 'force_authenticate')(user=self.staff_user)
        response = self.client.post(self.verify_url, {'ticket_code': 'TICKET_TEST_123456'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        resp_data = getattr(response, 'data', {})
        self.assertFalse(resp_data.get('success'))
        self.assertIn('đã được soát', resp_data.get('message', ''))

    def test_verify_ticket_expired_showtime(self):
        """Nhân viên quét mã vé có suất chiếu đã trôi qua -> 400 Bad Request & status_type EXPIRED_SHOWTIME"""
        past_showtime = Showtime.objects.create(
            movie=self.movie,
            room=self.room,
            show_date=timezone.now().date() - timedelta(days=1),
            start_time=time(10, 0),
            end_time=time(12, 0)
        )
        past_booking = Booking.objects.create(
            user=self.normal_user,
            showtime=past_showtime,
            total_price=100000.0,
            payment_status='PAID'
        )
        expired_ticket = Ticket.objects.create(
            booking=past_booking,
            seat=self.seat,
            price=100000.0,
            ticket_code="TICKET_EXPIRED_999",
            is_used=False
        )

        getattr(self.client, 'force_authenticate')(user=self.staff_user)
        response = self.client.post(self.verify_url, {'ticket_code': 'TICKET_EXPIRED_999'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        resp_data = getattr(response, 'data', {})
        self.assertFalse(resp_data.get('success'))
        self.assertEqual(resp_data.get('status_type'), 'EXPIRED_SHOWTIME')
        self.assertIn('SUẤT CHIẾU ĐÃ KẾT THÚC', resp_data.get('message', ''))
