from datetime import time, timedelta
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from CinemaBook.models import (
    Cinema, Room, Status, Movie, Showtime, Seat, Booking, Ticket, TypeTicket
)


class BookingAPITestCase(APITestCase):
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.booking_url = reverse('booking-list')

        self.user = User.objects.create_user(username='buyer', password='password123')
        self.type_ticket = TypeTicket.objects.create(name='Vé Thường', price=75000)

        self.status_ok = Status.objects.create(name="Active")
        self.cinema = Cinema.objects.create(name="Rạp BHS", location="Đà Nẵng")
        self.room = Room.objects.create(name="Phòng 3", capacity=40, cinema=self.cinema, status=self.status_ok)
        self.seat = Seat.objects.create(seat_number="B5", room=self.room, is_available=True)

        self.movie = Movie.objects.create(movie_name="Batman", duration=150)
        self.showtime = Showtime.objects.create(
            movie=self.movie, room=self.room,
            show_date=timezone.now().date() + timedelta(days=1),
            start_time=time(20, 0), end_time=time(22, 30)
        )

    def test_create_booking_success(self):
        """Test tạo đơn đặt vé với phương thức VNPAY thành công -> HTTP 201 Created"""
        getattr(self.client, 'force_authenticate')(user=self.user)
        payload = {
            'showtime': self.showtime.id,
            'ticket_items': [{'seat_id': self.seat.id, 'type_ticket_id': self.type_ticket.id}]
        }
        response = self.client.post(self.booking_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        resp_data = getattr(response, 'data', {})
        self.assertEqual(resp_data['payment_method'], 'VNPAY')

        booking = Booking.objects.filter(pk=resp_data['id']).first()
        self.assertIsNotNone(booking)
        self.assertEqual(booking.total_price, 75000.0)

        ticket = Ticket.objects.filter(booking=booking).first()
        self.assertIsNotNone(ticket)
        self.assertEqual(ticket.seat, self.seat)

    def test_create_vnpay_url(self):
        """Test khởi tạo đường dẫn thanh toán VNPay Sandbox -> HTTP 200 OK & chứa payment_url"""
        booking = Booking.objects.create(
            user=self.user, showtime=self.showtime, total_price=75000.0, payment_method='VNPAY'
        )
        url = reverse('booking-create-vnpay-url', kwargs={'pk': booking.id})
        getattr(self.client, 'force_authenticate')(user=self.user)
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        resp_data = getattr(response, 'data', {})
        self.assertIn('payment_url', resp_data)
        self.assertTrue(resp_data['payment_url'].startswith('http'))
