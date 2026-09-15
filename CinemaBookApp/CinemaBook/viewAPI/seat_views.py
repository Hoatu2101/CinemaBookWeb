from django.db import transaction
from django.utils import timezone
from django.core.cache import cache

from rest_framework import status, permissions, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import Seat, SeatShowtimeStatus, SeatStatus
from ..serializers import SeatSerializer, SeatShowtimeStatusSerializer


class SeatViewSet(viewsets.ReadOnlyModelViewSet):
    """API Danh sách ghế theo phòng"""
    queryset = Seat.objects.all().select_related('room')
    serializer_class = SeatSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = super().get_queryset()
        room_id = self.request.GET.get('room_id')
        return qs.filter(room_id=room_id) if room_id else qs


class SeatShowtimeStatusViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    """API Trạng thái ghế & Khóa ghế giữ chỗ tạm thời"""
    queryset = SeatShowtimeStatus.objects.all().select_related('seat', 'showtime', 'user')
    serializer_class = SeatShowtimeStatusSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = super().get_queryset()
        showtime_id = self.request.GET.get('showtime_id')
        return qs.filter(showtime_id=showtime_id) if showtime_id else qs

    @action(detail=False, methods=['post'])
    def lock_seats(self, request):
        """Khách hàng khóa giữ ghế tạm thời trước khi thanh toán (Cache RAM + DB Locking)"""
        showtime_id = request.data.get('showtime_id')
        seat_ids = request.data.get('seat_ids', [])
        user = request.user if request.user.is_authenticated else None
        client_session_id = request.data.get('client_session_id') or (f"user_{user.id}" if user else "anonymous")

        if not showtime_id or not seat_ids:
            return Response({'error': 'showtime_id và seat_ids là bắt buộc'}, status=status.HTTP_400_BAD_REQUEST)

        # Fast Path - RAM Cache Check (< 1ms)
        for s_id in seat_ids:
            lock_owner = cache.get(f"seat_lock:{showtime_id}:{s_id}")
            if lock_owner and lock_owner != client_session_id:
                return Response({'error': f'Ghế ID {s_id} đang được người khác chọn!'}, status=status.HTTP_400_BAD_REQUEST)

        locked = []
        with transaction.atomic():
            existing_locked = {
                s.seat_id: s for s in SeatShowtimeStatus.objects.select_for_update().filter(
                    showtime_id=showtime_id, seat_id__in=seat_ids
                )
            }
            now = timezone.now()
            for s_id in seat_ids:
                obj = existing_locked.get(s_id)
                if obj and obj.status == SeatStatus.BOOKED:
                    return Response({'error': f'Ghế ID {s_id} đã được đặt trước đó!'}, status=status.HTTP_400_BAD_REQUEST)
                
                if obj and obj.status == SeatStatus.LOCKED and obj.lock_time:
                    lock_owner = cache.get(f"seat_lock:{showtime_id}:{s_id}")
                    is_different_session = lock_owner and lock_owner != client_session_id
                    if is_different_session and (now - obj.lock_time).total_seconds() < 300:
                        return Response({'error': f'Ghế ID {s_id} đang được giữ chỗ ở một Tab hoặc trình duyệt khác trong 5 phút!'}, status=status.HTTP_400_BAD_REQUEST)
                
                if not obj:
                    obj = SeatShowtimeStatus.objects.create(
                        showtime_id=showtime_id, seat_id=s_id, user=user, status=SeatStatus.LOCKED, lock_time=now
                    )
                else:
                    obj.user, obj.status, obj.lock_time = user, SeatStatus.LOCKED, now
                    obj.save()

                cache.set(f"seat_lock:{showtime_id}:{s_id}", client_session_id, timeout=300)
                locked.append(obj.id)

        return Response({'message': 'Giữ ghế tạm thời thành công', 'locked_ids': locked}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def unlock_seats(self, request):
        """Khách hàng giải phóng/bỏ giữ ghế tạm thời"""
        showtime_id = request.data.get('showtime_id')
        seat_ids = request.data.get('seat_ids', [])

        if not showtime_id or not seat_ids:
            return Response({'error': 'showtime_id và seat_ids là bắt buộc'}, status=status.HTTP_400_BAD_REQUEST)

        for s_id in seat_ids:
            cache.delete(f"seat_lock:{showtime_id}:{s_id}")

        SeatShowtimeStatus.objects.filter(
            showtime_id=showtime_id, seat_id__in=seat_ids, status=SeatStatus.LOCKED
        ).delete()

        return Response({'message': 'Giải phóng ghế giữ chỗ thành công'}, status=status.HTTP_200_OK)
