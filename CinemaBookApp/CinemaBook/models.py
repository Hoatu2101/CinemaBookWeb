from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class Meta:
        db_table = 'categories'
        verbose_name_plural = 'Categories'
    def __str__(self):
        return self.name
class Status(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class Meta:
        db_table = 'status'
        verbose_name_plural = 'Statuses'

    def __str__(self):
        return self.name


class StatusMovie(models.Model):
    name_status = models.CharField(max_length=100)

    class Meta:
        db_table = 'status_movie'
        verbose_name_plural = 'Movie Statuses'

    def __str__(self):
        return self.name_status


class Movie(models.Model):
    movie_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    trailer = models.CharField(max_length=500, blank=True, null=True)
    duration = models.IntegerField(blank=True, null=True)
    poster = models.ImageField(upload_to='posters/', blank=True, null=True)
    active = models.BooleanField(default=True, blank=True, null=True)
    actor = models.CharField(max_length=255, blank=True, null=True)
    drirector = models.CharField(max_length=255, blank=True, null=True)
    release_year = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    categories = models.ManyToManyField(
        Category, related_name='movies', blank=True
    )
    status_movie = models.ForeignKey(
        StatusMovie, on_delete=models.SET_NULL, db_column='status_movie_id', blank=True, null=True, related_name='movies'
    )

    class Meta:
        db_table = 'movies'

    def __str__(self):
        return self.movie_name


class Cinema(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class Meta:
        db_table = 'cinemas'

    def __str__(self):
        return f"{self.name} - {self.location}"


class Room(models.Model):
    name = models.CharField(max_length=255)
    capacity = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    format=models.ForeignKey('MovieFormat', on_delete=models.SET_NULL, db_column='format_id', blank=True, null=True, related_name='rooms')
    cinema = models.ForeignKey(
        Cinema, on_delete=models.CASCADE, db_column='cinema_id', related_name='rooms'
    )
    status = models.ForeignKey(
        Status, on_delete=models.PROTECT, db_column='status_id', related_name='rooms'
    )

    class Meta:
        db_table = 'rooms'

    def clean(self):
        from .validate import validate_room
        validate_room(self)

    def __str__(self):
        cinema_name = self.cinema.name if self.cinema else "No Cinema"
        return f"{self.name} ({cinema_name})"

class SeatStatus(models.TextChoices):
    FREE = "FREE", "Free"
    LOCKED = "LOCKED", "Locked"
    BOOKED = "BOOKED", "Booked"

status = models.CharField(
    max_length=20,
    choices=SeatStatus.choices,
    default=SeatStatus.FREE
)


class Seat(models.Model):
    seat_number = models.CharField(max_length=10)
    is_available = models.BooleanField(default=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    room = models.ForeignKey(
        Room, on_delete=models.CASCADE, db_column='room_id', related_name='seats'
    )

    class Meta:
        db_table = 'seats'
        unique_together = (('room', 'seat_number'),)

    def clean(self):
        from .validate import validate_seat
        validate_seat(self)

    def __str__(self):
        room_name = self.room.name if self.room else "No Room"
        return f"Seat {self.seat_number} - Room {room_name}"


class Showtime(models.Model):
    show_date = models.DateField(blank=True, null=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    movie = models.ForeignKey(
        Movie, on_delete=models.CASCADE, db_column='movie_id', related_name='showtimes'
    )
    room = models.ForeignKey(
        Room, on_delete=models.CASCADE, db_column='room_id', related_name='showtimes'
    )
    class Meta:
        db_table = 'showtimes'

    def clean(self):
        from .validate import validate_showtime
        validate_showtime(self)

    def has_sold_seats(self):
        """Kiểm tra xem suất chiếu đã có ít nhất 1 ghế được bán/đặt vé hay chưa."""
        from .validate import check_showtime_has_sold_seats
        return check_showtime_has_sold_seats(self)

    def delete(self, using=None, keep_parents=False):
        from .validate import validate_showtime_deletion
        validate_showtime_deletion(self)
        return super().delete(using=using, keep_parents=keep_parents)

    def __str__(self):
        movie_name = self.movie.movie_name if self.movie else "No Movie"
        room_name = self.room.name if self.room else "No Room"
        date_str = self.show_date.strftime('%d/%m/%Y') if self.show_date else "N/A"
        start_str = self.start_time.strftime('%H:%M') if self.start_time else "N/A"
        end_str = self.end_time.strftime('%H:%M') if self.end_time else "N/A"
        return f"{movie_name} | {room_name} | Ngày {date_str} ({start_str} - {end_str})"
class UserRole(models.TextChoices):
    ADMIN = "ROLE_ADMIN", "Quản trị viên (Admin)"
    CINEMA_MANAGER = "ROLE_CINEMA_MANAGER", "Quản lý Rạp (Admin Nhánh)"
    USER = "ROLE_USER", "Khách hàng (User)"
    STAFF = "ROLE_STAFF", "Nhân viên (Staff)"


from django.contrib.auth.models import User as DjangoUser
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

User = DjangoUser  # Alias để các quan hệ Booking, SeatShowtimeStatus liên kết với DjangoUser


@receiver(pre_delete, sender=Showtime)
def prevent_showtime_delete_if_tickets_exist(sender, instance, **kwargs):
    from .validate import validate_showtime_deletion
    validate_showtime_deletion(instance)


class UserProfile(models.Model):
    user = models.OneToOneField(DjangoUser, on_delete=models.CASCADE, related_name='profile', verbose_name="Tài khoản hệ thống")
    role = models.CharField(max_length=50, choices=UserRole.choices, default=UserRole.USER, verbose_name="Vai trò (Role)")
    cinema = models.ForeignKey(
        Cinema, on_delete=models.SET_NULL, db_column='cinema_id', blank=True, null=True, related_name='staff_members', verbose_name="Rạp / Chi nhánh phụ trách"
    )

    name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Họ và tên")
    number_phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Số điện thoại")
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name="Ảnh đại diện")



    class Meta:
        db_table = 'user_profiles'
        verbose_name = "Thông tin mở rộng"
        verbose_name_plural = "Danh sách Thông tin mở rộng"

    def save(self, *args, **kwargs):
        if not self.pk and self.user_id:
            existing = UserProfile.objects.filter(user_id=self.user_id).first()
            if existing:
                self.pk = existing.pk
                self._state.adding = False
        super().save(*args, **kwargs)
        if self.user:
            should_be_staff = self.role in [UserRole.ADMIN, UserRole.CINEMA_MANAGER, UserRole.STAFF]
            if not self.user.is_superuser and self.user.is_staff != should_be_staff:
                self.user.is_staff = should_be_staff
                self.user.save(update_fields=['is_staff'])

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"



@receiver(post_save, sender=DjangoUser)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """Tự động khởi tạo hoặc cập nhật UserProfile khi một Django User được tạo/lưu."""
    if created:
        UserProfile.objects.create(user=instance)
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()
        else:
            UserProfile.objects.create(user=instance)



class MovieFormat(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class Meta:
        db_table = 'movie_formats'

    def __str__(self):
        return self.name
class SeatShowtimeStatus(models.Model):
    showtime = models.ForeignKey(
        Showtime, on_delete=models.CASCADE, db_column='showtime_id', related_name='seat_statuses'
    )
    seat = models.ForeignKey(
        Seat, on_delete=models.CASCADE, db_column='seat_id', related_name='showtime_statuses'
    )
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, db_column='user_id', blank=True, null=True, related_name='locked_seats'
    )
    status = models.CharField(max_length=20)
    lock_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'seat_showtime_status'
        unique_together = (('showtime', 'seat'),)

    def __str__(self):
        return f"Showtime {self.showtime_id} - Seat {self.seat_id}: {self.status}"

class paymentMethod(models.TextChoices):
    CASH = "CASH", "Cash"
    CREDIT_CARD = "CREDIT_CARD", "Credit Card"
    PAYPAL = "PAYPAL", "PayPal"
    ZALO_PAY = "ZALO_PAY", "Zalo Pay"
    MOMO = "MOMO", "MoMo"
class PaymentStatus(models.TextChoices):
    PENDING = "PENDING"
    PAID = "PAID"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
class Booking(models.Model):
    total_price = models.FloatField(default=0.0)
    payment_method = models.CharField(max_length=50, choices=paymentMethod.choices, default=paymentMethod.CASH)
    payment_status = models.CharField(max_length=50, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    showtime = models.ForeignKey(
        Showtime, on_delete=models.CASCADE, db_column='showtime_id', related_name='bookings'
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, db_column='user_id', related_name='bookings'
    )

    class Meta:
        db_table = 'bookings'
        ordering = ['-created_at', '-id']

    def __str__(self):
        return f"Booking #{self.id} - User {self.user.username} - {self.total_price} VNĐ ({self.payment_status})"

    @property
    def movie(self):
        return self.showtime.movie if self.showtime else None

    @property
    def showtime_date(self):
        return self.showtime.show_date.strftime('%d/%m/%Y') if (self.showtime and self.showtime.show_date) else None

    @property
    def showtime_time(self):
        if self.showtime and self.showtime.start_time and self.showtime.end_time:
            return f"{self.showtime.start_time.strftime('%H:%M')} - {self.showtime.end_time.strftime('%H:%M')}"
        return None

class TypeTicket(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    price = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class Meta:
        db_table = 'type_tickets'

    def __str__(self):
        return f"{self.name} - {self.price} VNĐ"





class Ticket(models.Model):
    ticket_code = models.CharField(max_length=50, unique=True, blank=True, null=True, verbose_name="Mã vé")
    price = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    booking = models.ForeignKey(
        Booking, on_delete=models.CASCADE, db_column='booking_id', related_name='tickets'
    )
    seat = models.ForeignKey(
        Seat, on_delete=models.PROTECT, db_column='seat_id', related_name='tickets'
    )
    type_ticket = models.ForeignKey(
        TypeTicket, on_delete=models.PROTECT, db_column='type_ticket_id', blank=True, null=True, related_name='tickets'
    )
    is_used = models.BooleanField(default=False, verbose_name="Đã soát vé")
    used_at = models.DateTimeField(blank=True, null=True, verbose_name="Thời gian soát vé")

    class Meta:
        db_table = 'tickets'

    def save(self, *args, **kwargs):
        if not self.ticket_code:
            import uuid
            self.ticket_code = f"TK-{uuid.uuid4().hex[:8].upper()}"
        if self.type_ticket and self.type_ticket.price is not None:
            self.price = self.type_ticket.price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Ticket #{self.id} ({self.ticket_code}) - Booking #{self.booking_id}"

