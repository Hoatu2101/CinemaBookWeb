from django.utils import timezone
from rest_framework import status, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import Showtime, Seat, SeatShowtimeStatus, Ticket, SeatStatus
from ..serializers import ShowtimeSerializer


class ShowtimeViewSet(viewsets.ReadOnlyModelViewSet):
    """API Suất chiếu & Sơ đồ ghế khách hàng"""
    queryset = Showtime.objects.all().select_related('movie', 'room', 'room__cinema')
    serializer_class = ShowtimeSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = super().get_queryset()
        p = self.request.GET
        if p.get('movie_id'):
            qs = qs.filter(movie_id=p['movie_id'])
        if p.get('cinema_id'):
            qs = qs.filter(room__cinema_id=p['cinema_id'])
        if p.get('show_date'):
            qs = qs.filter(show_date=p['show_date'])
        return qs

    @action(detail=True, methods=['get'])
    def seats(self, request, pk=None):
        """Trả về sơ đồ ghế của phòng và trạng thái từng ghế cho suất chiếu này"""
        showtime = self.get_object()
        room_seats = Seat.objects.filter(room=showtime.room)

        # Giải phóng ghế giữ quá 5 phút (300s)
        SeatShowtimeStatus.objects.filter(
            showtime=showtime,
            status=SeatStatus.LOCKED,
            lock_time__lt=timezone.now() - timezone.timedelta(seconds=300)
        ).delete()

        status_objs = {sss.seat_id: sss for sss in SeatShowtimeStatus.objects.filter(showtime=showtime)}
        booked_ticket_seat_ids = set(
            Ticket.objects.filter(
                booking__showtime=showtime,
                booking__payment_status__in=['PAID', 'PENDING', 'COMPLETED']
            ).values_list('seat_id', flat=True)
        )

        user = request.user if request.user.is_authenticated else None
        result = []
        for s in room_seats:
            sss_obj = status_objs.get(s.id)
            if s.id in booked_ticket_seat_ids or (sss_obj and sss_obj.status == SeatStatus.BOOKED):
                seat_stat = SeatStatus.BOOKED
            elif sss_obj and sss_obj.status == SeatStatus.LOCKED:
                seat_stat = SeatStatus.FREE if (sss_obj.user and user and sss_obj.user == user) else SeatStatus.LOCKED
            else:
                seat_stat = SeatStatus.FREE if s.is_available else "UNAVAILABLE"

            result.append({
                'id': s.id,
                'seat_number': s.seat_number,
                'is_available': s.is_available,
                'status': seat_stat,
                'locked_user_id': sss_obj.user_id if sss_obj else None
            })

        return Response({
            'showtime_id': showtime.id,
            'room_id': showtime.room_id,
            'room_name': showtime.room.name,
            'total_seats': len(result),
            'seats': result
        }, status=status.HTTP_200_OK)
