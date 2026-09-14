from datetime import time, timedelta
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from CinemaBook.models import (
    Cinema, Room, Status, Movie, Showtime, Seat, SeatShowtimeStatus, SeatStatus
)


class SeatLockingTestCase(APITestCase):
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.lock_url = reverse('seat-status-lock-seats')
        self.unlock_url = reverse('seat-status-unlock-seats')

        self.user1 = User.objects.create_user(username='user1', password='password123')
        self.user2 = User.objects.create_user(username='user2', password='password123')

        self.status_ok = Status.objects.create(name="Active")
        self.cinema = Cinema.objects.create(name="Rạp Lotte", location="Hà Nội")
        self.room = Room.objects.create(name="Phòng A", capacity=30, cinema=self.cinema, status=self.status_ok)
        self.seat1 = Seat.objects.create(seat_number="A1", room=self.room, is_available=True)
        self.seat2 = Seat.objects.create(seat_number="A2", room=self.room, is_available=True)

        self.movie = Movie.objects.create(movie_name="Avengers Endgame", duration=180)
        self.showtime = Showtime.objects.create(
            movie=self.movie, room=self.room,
            show_date=timezone.now().date() + timedelta(days=1),
            start_time=time(14, 0), end_time=time(17, 0)
        )

    def test_lock_seats_success(self):
        """Test User1 khóa giữ ghế A1 thành công -> HTTP 200 OK"""
        getattr(self.client, 'force_authenticate')(user=self.user1)
        payload = {'showtime_id': self.showtime.id, 'seat_ids': [self.seat1.id]}
        response = self.client.post(self.lock_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        resp_data = getattr(response, 'data', {})
        self.assertIn('locked_ids', resp_data)

        sss = SeatShowtimeStatus.objects.filter(showtime=self.showtime, seat=self.seat1).first()
        self.assertIsNotNone(sss)
        self.assertEqual(sss.status, SeatStatus.LOCKED)
        self.assertEqual(sss.user, self.user1)

    def test_lock_seats_already_locked_by_other_user(self):
        """Test User2 cố gắng giữ ghế đã bị User1 khóa -> HTTP 400 Bad Request"""
        SeatShowtimeStatus.objects.create(
            showtime=self.showtime, seat=self.seat1, user=self.user1,
            status=SeatStatus.LOCKED, lock_time=timezone.now()
        )

        getattr(self.client, 'force_authenticate')(user=self.user2)
        payload = {'showtime_id': self.showtime.id, 'seat_ids': [self.seat1.id]}
        response = self.client.post(self.lock_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unlock_seats_success(self):
        """Test mở khóa giải phóng ghế giữ chỗ -> HTTP 200 OK & xóa khỏi DB"""
        SeatShowtimeStatus.objects.create(
            showtime=self.showtime, seat=self.seat1, user=self.user1,
            status=SeatStatus.LOCKED, lock_time=timezone.now()
        )

        getattr(self.client, 'force_authenticate')(user=self.user1)
        payload = {'showtime_id': self.showtime.id, 'seat_ids': [self.seat1.id]}
        response = self.client.post(self.unlock_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        sss = SeatShowtimeStatus.objects.filter(showtime=self.showtime, seat=self.seat1).first()
        self.assertIsNone(sss)
