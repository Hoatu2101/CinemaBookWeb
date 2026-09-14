from django.db import transaction
from django.utils import timezone
from django.contrib.auth.models import User

from rest_framework import status, permissions, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import Booking, Ticket, Showtime, SeatShowtimeStatus, TypeTicket, SeatStatus
from ..serializers import TypeTicketSerializer, BookingSerializer, TicketSerializer
from ..Service.VNpayservices import VNPayService
from .staff_views import is_staff_member


class TypeTicketViewSet(viewsets.ReadOnlyModelViewSet):
    """API Loại vé (Vé thường, VIP, Sinh viên...)"""
    queryset = TypeTicket.objects.all()
    serializer_class = TypeTicketSerializer
    permission_classes = [permissions.AllowAny]


class BookingViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin):
    """API Khách hàng Tạo đơn đặt vé & Quản lý đơn vé (Thanh toán Online VNPAY)"""
    queryset = Booking.objects.all().select_related(
        'user', 'showtime', 'showtime__movie', 'showtime__room'
    ).prefetch_related('tickets', 'tickets__seat', 'tickets__type_ticket')
    serializer_class = BookingSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_authenticated and not is_staff_member(user):
            qs = qs.filter(user=user)

        p = self.request.GET
        if p.get('user_id'):
            qs = qs.filter(user_id=p['user_id'])
        if p.get('showtime_id'):
            qs = qs.filter(showtime_id=p['showtime_id'])
        if p.get('payment_status'):
            qs = qs.filter(payment_status=p['payment_status'])
        return qs.order_by('-created_at', '-id')

    def create(self, request, *args, **kwargs):
        """Khách hàng tiến hành Đặt vé / Tạo Đơn hàng mới (Thanh toán Online VNPay)"""
        data = request.data
        showtime_id = data.get('showtime')
        # Hệ thống duy nhất hỗ trợ phương thức Thanh Toán Online (VNPAY)
        payment_method = 'VNPAY'
        ticket_items = data.get('ticket_items', [])
        seat_ids = data.get('seat_ids', [])

        if not showtime_id:
            return Response({'error': 'Trường showtime là bắt buộc'}, status=status.HTTP_400_BAD_REQUEST)

        if not ticket_items and seat_ids:
            default_type = TypeTicket.objects.first()
            type_id = default_type.id if default_type else None
            ticket_items = [{'seat_id': sid, 'type_ticket_id': type_id} for sid in seat_ids]

        if not ticket_items:
            return Response({'error': 'Vui lòng chọn ít nhất một ghế để đặt vé'}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user if request.user.is_authenticated else None
        user_id = data.get('user') or (user.id if user else None)
        if not user_id:
            first_user = User.objects.first()
            user_id = first_user.id if first_user else None

        if not user_id:
            return Response({'error': 'Chưa xác định tài khoản người dùng đặt vé'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                showtime = Showtime.objects.get(pk=showtime_id)
                total_price = 0.0
                tickets_to_create = []

                target_seat_ids = [item.get('seat_id') for item in ticket_items if item.get('seat_id')]
                locked_statuses = {
                    s.seat_id: s for s in SeatShowtimeStatus.objects.select_for_update().filter(
                        showtime=showtime, seat_id__in=target_seat_ids
                    )
                }

                for item in ticket_items:
                    s_id = item.get('seat_id')
                    t_type_id = item.get('type_ticket_id')

                    existing_status = locked_statuses.get(s_id)
                    is_booked = existing_status and existing_status.status == SeatStatus.BOOKED
                    existing_ticket = Ticket.objects.filter(
                        booking__showtime=showtime, seat_id=s_id, booking__payment_status__in=['PAID', 'PENDING', 'COMPLETED']
                    ).first()
                    if is_booked or existing_ticket:
                        return Response({'error': f'Ghế ID {s_id} đã được người khác đặt trước cho suất chiếu này!'}, status=status.HTTP_400_BAD_REQUEST)

                    type_ticket = TypeTicket.objects.filter(pk=t_type_id).first() if t_type_id else None
                    price = float(type_ticket.price) if (type_ticket and type_ticket.price) else 75000.0

                    total_price += price
                    tickets_to_create.append({'seat_id': s_id, 'type_ticket': type_ticket, 'price': price})

                booking = Booking.objects.create(
                    user_id=user_id,
                    showtime=showtime,
                    payment_method=payment_method,
                    payment_status='PENDING',
                    total_price=total_price
                )

                now = timezone.now()
                for t_info in tickets_to_create:
                    Ticket.objects.create(
                        booking=booking,
                        seat_id=t_info['seat_id'],
                        type_ticket=t_info['type_ticket'],
                        price=t_info['price']
                    )
                    SeatShowtimeStatus.objects.update_or_create(
                        showtime=showtime,
                        seat_id=t_info['seat_id'],
                        defaults={'user_id': user_id, 'status': SeatStatus.LOCKED, 'lock_time': now}
                    )

                return Response(self.get_serializer(booking).data, status=status.HTTP_201_CREATED)

        except Showtime.DoesNotExist:
            return Response({'error': 'Không tìm thấy Suất chiếu!'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Khách hàng Hủy đơn đặt vé & Giải phóng ghế"""
        booking = self.get_object()
        if booking.payment_status == 'PAID':
            return Response({'message': 'Vé đã thanh toán thành công không được phép hủy!'}, status=status.HTTP_400_BAD_REQUEST)
        if booking.payment_status == 'CANCELLED':
            return Response({'message': 'Đơn hàng này đã được hủy trước đó!'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            booking.payment_status = 'CANCELLED'
            booking.save()
            for t in booking.tickets.all():
                SeatShowtimeStatus.objects.filter(showtime=booking.showtime, seat=t.seat).update(status=SeatStatus.FREE, user=None)

        return Response({'message': 'Hủy đơn vé thành công! Ghế đã được giải phóng.'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post', 'get'])
    def create_vnpay_url(self, request, pk=None):
        """API Tạo đường dẫn Thanh toán VNPay Sandbox cho Đơn vé"""
        try:
            booking = self.get_object()
            ip_addr = request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('REMOTE_ADDR', '127.0.0.1')
            if ',' in ip_addr:
                ip_addr = ip_addr.split(',')[0].strip()

            payment_url = VNPayService().get_payment_url(
                order_id=booking.id,
                amount=booking.total_price,
                order_info=f"Thanh toan ve xem phim CineBook #{booking.id}",
                ip_addr=ip_addr
            )
            return Response({'booking_id': booking.id, 'total_price': booking.total_price, 'payment_url': payment_url}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class TicketViewSet(viewsets.ReadOnlyModelViewSet):
    """API Vé của Khách hàng & Kiểm tra Mã vé / QR Code"""
    queryset = Ticket.objects.all().select_related(
        'booking', 'booking__showtime', 'booking__showtime__movie', 'seat', 'type_ticket'
    )
    serializer_class = TicketSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = super().get_queryset()
        booking_id = self.request.GET.get('booking_id')
        return qs.filter(booking_id=booking_id) if booking_id else qs

    @action(detail=False, methods=['post'])
    def verify(self, request):
        """API Soát vé từ mã QR Code / Mã vé"""
        if not request.user or not request.user.is_authenticated:
            return Response({'error': 'Bạn cần đăng nhập để thực hiện soát vé'}, status=status.HTTP_401_UNAUTHORIZED)

        if not is_staff_member(request.user):
            return Response({'error': 'Quyền truy cập bị từ chối. Chỉ nhân viên mới có quyền soát vé!'}, status=status.HTTP_403_FORBIDDEN)

        ticket_code = request.data.get('ticket_code', '').strip()
        if not ticket_code:
            return Response({'error': 'Mã vé (ticket_code) là bắt buộc'}, status=status.HTTP_400_BAD_REQUEST)

        ticket = Ticket.objects.filter(ticket_code__iexact=ticket_code).first()
        if not ticket:
            return Response({'error': 'Không tìm thấy mã vé trên hệ thống'}, status=status.HTTP_404_NOT_FOUND)

        if ticket.is_used:
            return Response({'success': False, 'message': 'Vé này đã được soát trước đó!', 'used_at': ticket.used_at}, status=status.HTTP_400_BAD_REQUEST)

        ticket.is_used = True
        ticket.used_at = timezone.now()
        ticket.save()

        return Response({
            'success': True,
            'message': 'Soát vé thành công!',
            'ticket_code': ticket.ticket_code,
            'movie_name': ticket.booking.showtime.movie.movie_name if (ticket.booking and ticket.booking.showtime) else '',
            'seat_number': ticket.seat.seat_number if ticket.seat else ''
        }, status=status.HTTP_200_OK)
