from datetime import time, timedelta
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from CinemaBook.models import (
    Cinema, Room, Status, Movie, Showtime, Seat, SeatShowtimeStatus, SeatStatus, Category
)


class MovieAndShowtimeAPITestCase(APITestCase):
    def setUp(self):
        super().setUp()
        self.client = APIClient()

        self.category = Category.objects.create(name="Hành Động", description="Phim hành động kịch tính")
        self.status_ok = Status.objects.create(name="Available")
        self.cinema = Cinema.objects.create(name="Rạp CGV Landmark", location="HCM")
        self.room = Room.objects.create(name="Phòng IMAX", capacity=50, cinema=self.cinema, status=self.status_ok)

        self.movie1 = Movie.objects.create(
            movie_name="Spider-Man No Way Home",
            duration=148,
            active=True
        )
        self.movie1.categories.add(self.category)
        self.movie2 = Movie.objects.create(
            movie_name="Dune Part Two",
            duration=166,
            active=True
        )

        self.seat1 = Seat.objects.create(seat_number="A1", room=self.room, is_available=True)
        self.seat2 = Seat.objects.create(seat_number="A2", room=self.room, is_available=True)

        self.showtime = Showtime.objects.create(
            movie=self.movie1,
            room=self.room,
            show_date=timezone.now().date() + timedelta(days=1),
            start_time=time(18, 0),
            end_time=time(20, 30)
        )

        self.movie_list_url = reverse('movie-list')
        self.category_list_url = reverse('category-list')
        self.showtime_list_url = reverse('showtime-list')
        self.showtime_seats_url = reverse('showtime-seats', kwargs={'pk': self.showtime.id})

    def test_list_movies_success(self):
        """Test API danh sách phim -> 200 OK & trả về đúng các phim active"""
        response = self.client.get(self.movie_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        resp_data = getattr(response, 'data', {})
        results = resp_data.get('results', resp_data) if isinstance(resp_data, dict) else resp_data
        self.assertGreaterEqual(len(results), 2)

    def test_filter_movies_by_category(self):
        """Test lọc phim theo thể loại category_id -> 200 OK"""
        response = self.client.get(f"{self.movie_list_url}?category_id={self.category.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        resp_data = getattr(response, 'data', {})
        results = resp_data.get('results', resp_data) if isinstance(resp_data, dict) else resp_data
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['movie_name'], "Spider-Man No Way Home")

    def test_list_categories(self):
        """Test API danh sách thể loại phim -> 200 OK"""
        response = self.client.get(self.category_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        resp_data = getattr(response, 'data', {})
        results = resp_data.get('results', resp_data) if isinstance(resp_data, dict) else resp_data
        self.assertGreaterEqual(len(results), 1)

    def test_list_showtimes_with_filters(self):
        """Test lọc danh sách suất chiếu theo movie_id & cinema_id -> 200 OK"""
        url = f"{self.showtime_list_url}?movie_id={self.movie1.id}&cinema_id={self.cinema.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        resp_data = getattr(response, 'data', {})
        results = resp_data.get('results', resp_data) if isinstance(resp_data, dict) else resp_data
        self.assertEqual(len(results), 1)

    def test_get_showtime_seats_map(self):
        """Test lấy sơ đồ ghế của suất chiếu -> 200 OK & trả về danh sách ghế"""
        response = self.client.get(self.showtime_seats_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        resp_data = getattr(response, 'data', {})
        self.assertEqual(resp_data['showtime_id'], self.showtime.id)
        self.assertEqual(resp_data['total_seats'], 2)

    def test_showtime_seats_auto_expire_expired_locks(self):
        """Test tự động giải phóng các ghế giữ quá 300s khi gọi API sơ đồ ghế"""
        expired_time = timezone.now() - timedelta(seconds=400)
        SeatShowtimeStatus.objects.create(
            showtime=self.showtime,
            seat=self.seat1,
            status=SeatStatus.LOCKED,
            lock_time=expired_time
        )
        self.assertTrue(SeatShowtimeStatus.objects.filter(showtime=self.showtime, seat=self.seat1).exists())

        response = self.client.get(self.showtime_seats_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(SeatShowtimeStatus.objects.filter(showtime=self.showtime, seat=self.seat1).exists())
