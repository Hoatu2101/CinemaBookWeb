import json
from django import forms
from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import path
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from django.contrib.auth.models import User as DjangoUser
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import (
    Category, MovieFormat, Status, StatusMovie, Movie, Cinema, Room, Seat,
    Showtime, TypeTicket, UserProfile, SeatShowtimeStatus, Booking, Ticket, UserRole
)
from .validate import validate_showtime, validate_showtime_deletion, check_showtime_has_sold_seats

admin.site.site_header = "CineBook System"
admin.site.site_title = "CineBook"
admin.site.index_title = "Hệ thống Quản lý CineBook"


def is_branch_admin(user):
    """Kiểm tra user có phải Admin Nhánh / Quản lý rạp hay không (không phải superuser và có rạp phụ trách)"""
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return False
    if hasattr(user, 'profile') and user.profile.cinema:
        return True
    return False


def get_user_cinema(user):
    """Lấy rạp do user phụ trách"""
    if hasattr(user, 'profile'):
        return user.profile.cinema
    return None



@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_per_page = 20
    list_display = ('id', 'name', 'description', 'created_at')
    list_filter = ('name', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('-created_at',)

    def has_module_permission(self, request):
        if is_branch_admin(request.user):
            return False
        return super().has_module_permission(request)


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_per_page = 20
    list_display = ('id', 'name', 'description', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name',)

    def has_module_permission(self, request):
        if is_branch_admin(request.user):
            return False
        return super().has_module_permission(request)


@admin.register(StatusMovie)
class StatusMovieAdmin(admin.ModelAdmin):
    list_per_page = 20
    list_display = ('id', 'name_status',)
    list_filter = ('name_status',)
    search_fields = ('name_status',)

    def has_module_permission(self, request):
        if is_branch_admin(request.user):
            return False
        return super().has_module_permission(request)


class MovieAdminForm(forms.ModelForm):
    class Meta:
        model = Movie
        fields = '__all__'
        widgets = {
            'movie_name': forms.TextInput(attrs={'placeholder': 'Nhập tên phim...', 'style': 'font-size: 1.1rem; font-weight: 600;'}),
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Nhập tóm tắt nội dung phim...'}),
            'trailer': forms.URLInput(attrs={'placeholder': 'https://www.youtube.com/watch?v=...'}),
            'actor': forms.TextInput(attrs={'placeholder': 'Tên các diễn viên'}),
            'drirector': forms.TextInput(attrs={'placeholder': 'Tên đạo diễn'}),
        }

    def clean_release_year(self):
        release_year = self.cleaned_data.get('release_year')
        if release_year is not None and (release_year < 1900 or release_year > 2100):
            raise forms.ValidationError('Vui lòng nhập năm hợp lệ (từ 1900 đến 2100).')
        return release_year


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_per_page = 20
    form = MovieAdminForm
    change_form_template = 'admin/CinemaBook/movie/change_form.html'
    list_display = ('id', 'movie_name', 'movie_poster', 'duration', 'active', 'release_year', 'actor', 'view_detail')
    list_filter = ('active', 'status_movie', 'categories', 'release_year', 'created_at')
    search_fields = ('movie_name', 'description', 'actor', 'drirector')
    ordering = ('-created_at',)
    filter_horizontal = ('categories',)

    def has_module_permission(self, request):
        if is_branch_admin(request.user):
            return False
        return super().has_module_permission(request)

    @admin.display(description='Poster')
    def movie_poster(self, obj):
        if obj.poster:
            return format_html(
                '<img src="{}" width="70" height="90" style="object-fit:cover;border-radius:8px;box-shadow:0 4px 10px rgba(0,0,0,0.3);" />',
                obj.poster.url
            )
        return "-"

    @admin.display(description='Thao tác')
    def view_detail(self, obj):
        url = f"/admin/CinemaBook/movie/{obj.id}/change/"
        return format_html(
            '<a href="{}" style="background: linear-gradient(135deg, #e11d48, #be123c); color: #ffffff; padding: 5px 14px; border-radius: 8px; font-weight: 700; font-size: 0.8rem; text-decoration: none; display: inline-flex; align-items: center; box-shadow: 0 4px 10px rgba(225, 29, 72, 0.35);">Xem chi tiết</a>',
            url
        )



@admin.register(MovieFormat)
class MovieFormatAdmin(admin.ModelAdmin):
    list_per_page = 20
    list_display = ('id', 'name', 'description', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('created_at',)
    ordering = ('-created_at',)

    def has_module_permission(self, request):
        if is_branch_admin(request.user):
            return False
        return super().has_module_permission(request)


# -------------------------------------------------------------
# CỤM RẠP & PHÒNG CHIẾU & GHẾ (Phân quyền theo Rạp)
# -------------------------------------------------------------

class RoomInline(admin.TabularInline):
    model = Room
    extra = 0
    can_delete = False
    fields = ('name', 'get_capacity', 'get_format', 'get_status', 'edit_room')
    readonly_fields = ('name', 'get_capacity', 'get_format', 'get_status', 'edit_room')
    verbose_name = "Phòng chiếu"
    verbose_name_plural = "Danh sách Phòng chiếu thuộc Rạp này"

    @admin.display(description='Sức chứa')
    def get_capacity(self, obj):
        return format_html(
            '<span style="font-weight: 700; color: #ffffff; font-size: 0.9rem;">{} ghế</span>',
            obj.capacity
        )

    @admin.display(description='Định dạng')
    def get_format(self, obj):
        if obj.format:
            return format_html(
                '<span style="background: rgba(139, 92, 246, 0.18); color: #c084fc; border: 1px solid rgba(139, 92, 246, 0.4); padding: 4px 12px; border-radius: 20px; font-weight: 700; font-size: 0.82rem; display: inline-block;">{}</span>',
                obj.format.name
            )
        return mark_safe('<span style="color: #71717a;">-</span>')

    @admin.display(description='Trạng thái')
    def get_status(self, obj):
        if obj.status:
            status_name = obj.status.name
            is_active = "dụng" in status_name.lower() or "động" in status_name.lower() or "active" in status_name.lower()
            color = "#10b981" if is_active else "#f43f5e"
            bg = "rgba(16, 185, 129, 0.15)" if is_active else "rgba(244, 63, 94, 0.15)"
            border = "rgba(16, 185, 129, 0.4)" if is_active else "rgba(244, 63, 94, 0.4)"
            return format_html(
                '<span style="background: {}; color: {}; border: 1px solid {}; padding: 4px 12px; border-radius: 20px; font-weight: 700; font-size: 0.82rem; display: inline-block;">{}</span>',
                bg, color, border, status_name
            )
        return mark_safe('<span style="color: #71717a;">-</span>')

    @admin.display(description='Thao tác')
    def edit_room(self, obj):
        if obj.pk:
            url = f"/admin/CinemaBook/room/{obj.pk}/change/"
            return format_html(
                '<a href="{}" style="background: linear-gradient(135deg, #e11d48, #be123c); color: #ffffff; padding: 6px 14px; border-radius: 8px; font-weight: 700; font-size: 0.8rem; text-decoration: none; display: inline-flex; align-items: center; gap: 6px; box-shadow: 0 4px 12px rgba(225, 29, 72, 0.35);">⚙️ Xem phòng & Ghế</a>',
                url
            )
        return "-"

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Cinema)
class CinemaAdmin(admin.ModelAdmin):
    list_per_page = 20
    list_display = ('id', 'name', 'location', 'get_room_count', 'created_at', 'view_detail')
    list_filter = ('name', 'location', 'created_at')
    search_fields = ('name', 'location')
    ordering = ('-created_at',)
    inlines = [RoomInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if is_branch_admin(request.user):
            cinema = get_user_cinema(request.user)
            return qs.filter(id=cinema.id if cinema else None)
        return qs

    def has_add_permission(self, request):
        if is_branch_admin(request.user):
            return False
        return super().has_add_permission(request)

    def has_change_permission(self, request, obj=None):
        if is_branch_admin(request.user):
            return False
        return super().has_change_permission(request, obj)

    def has_view_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        if is_branch_admin(request.user):
            return False
        return super().has_delete_permission(request, obj)

    @admin.display(description='Số lượng phòng chiếu')
    def get_room_count(self, obj):
        return obj.rooms.count()

    @admin.display(description='Thao tác')
    def view_detail(self, obj):
        url = f"/admin/CinemaBook/cinema/{obj.id}/change/"
        return format_html(
            '<a href="{}" style="background: linear-gradient(135deg, #e11d48, #be123c); color: #ffffff; padding: 5px 14px; border-radius: 8px; font-weight: 700; font-size: 0.8rem; text-decoration: none; display: inline-flex; align-items: center; box-shadow: 0 4px 10px rgba(225, 29, 72, 0.35);">Xem chi tiết</a>',
            url
        )



class RoomAdminForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean() or {}
        room = Room(
            pk=self.instance.pk if self.instance else None,
            name=cleaned_data.get('name'),
            capacity=cleaned_data.get('capacity'),
            cinema=cleaned_data.get('cinema'),
            status=cleaned_data.get('status'),
            format=cleaned_data.get('format'),
        )
        try:
            from .validate import validate_room
            validate_room(room)
        except ValidationError as exc:
            raise forms.ValidationError(exc.messages)
        return cleaned_data


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_per_page = 20
    form = RoomAdminForm
    change_form_template = 'admin/CinemaBook/room/change_form.html'
    list_display = ('id', 'name', 'capacity', 'cinema', 'status', 'format')
    list_filter = ('cinema', 'format', 'status', 'created_at')
    search_fields = ('name', 'cinema__name', 'cinema__location')
    ordering = ('-created_at',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if is_branch_admin(request.user):
            cinema = get_user_cinema(request.user)
            return qs.filter(cinema=cinema)
        return qs

    def has_add_permission(self, request):
        if is_branch_admin(request.user):
            return False
        return super().has_add_permission(request)

    def has_change_permission(self, request, obj=None):
        if is_branch_admin(request.user):
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if is_branch_admin(request.user):
            return False
        return super().has_delete_permission(request, obj)

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        if obj:
            seats = list(obj.seats.values('id', 'seat_number', 'is_available'))
            context['room_seats'] = seats
            context['room_seats_json'] = json.dumps(seats)
        else:
            context['room_seats'] = []
            context['room_seats_json'] = json.dumps([])
        return super().render_change_form(request, context, add, change, form_url, obj)


class SeatAdminForm(forms.ModelForm):
    class Meta:
        model = Seat
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean() or {}
        room = cleaned_data.get('room')
        seat_number = cleaned_data.get('seat_number')
        if room and seat_number:
            seat = Seat(
                pk=self.instance.pk if self.instance else None,
                seat_number=seat_number,
                is_available=cleaned_data.get('is_available', True),
                room=room,
            )
            try:
                from .validate import validate_seat
                validate_seat(seat)
            except ValidationError as exc:
                raise forms.ValidationError(exc.messages)
        return cleaned_data


@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_per_page = 20
    form = SeatAdminForm
    change_form_template = 'admin/CinemaBook/seat/change_form.html'
    list_display = ('id', 'seat_number', 'room', 'is_available', 'created_at')
    list_filter = ('room__cinema', 'room', 'is_available', 'created_at')
    search_fields = ('seat_number', 'room__name', 'room__cinema__name')
    ordering = ('-created_at',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if is_branch_admin(request.user):
            cinema = get_user_cinema(request.user)
            return qs.filter(room__cinema=cinema)
        return qs

    def has_module_permission(self, request):
        if is_branch_admin(request.user):
            return False
        return super().has_module_permission(request)

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        rooms_data = {}
        for room in Room.objects.prefetch_related('seats').all():
            seats = list(room.seats.values('id', 'seat_number', 'is_available'))
            rooms_data[str(room.id)] = {
                'name': room.name,
                'cinema': room.cinema.name if room.cinema else '',
                'capacity': room.capacity,
                'seats': seats
            }
        context['rooms_seat_map_json'] = json.dumps(rooms_data)
        return super().render_change_form(request, context, add, change, form_url, obj)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('batch-create/', self.admin_site.admin_view(self.batch_create_seats), name='seat_batch_create'),
        ]
        return custom_urls + urls

    def batch_create_seats(self, request):
        if request.method == 'POST':
            room_id = request.POST.get('room_id')
            try:
                rows = int(request.POST.get('num_rows', 6))
                cols = int(request.POST.get('num_cols', 10))
            except ValueError:
                rows, cols = 6, 10

            if not room_id:
                return JsonResponse({'status': 'error', 'message': 'Vui lòng chọn một phòng chiếu trước khi tạo ghế!'}, status=400)

            row_letters = [chr(65 + i) for i in range(rows)]

            try:
                room = Room.objects.get(pk=room_id)

                candidate_seat_numbers = [f"{r}{c}" for r in row_letters for c in range(1, cols + 1)]
                existing_seat_numbers = set(Seat.objects.filter(room=room).values_list('seat_number', flat=True))
                new_seat_numbers = [sn for sn in candidate_seat_numbers if sn not in existing_seat_numbers]

                current_count = len(existing_seat_numbers)
                to_create_count = len(new_seat_numbers)

                if current_count + to_create_count > room.capacity:
                    return JsonResponse({
                        'status': 'error',
                        'message': f"Không thể tạo thêm {to_create_count} ghế! Tổng số ghế ({current_count + to_create_count}) sẽ vượt quá sức chứa tối đa của phòng '{room.name}' ({room.capacity} ghế). Hiện tại phòng đã có {current_count} ghế."
                    }, status=400)

                created_count = 0
                for seat_num in candidate_seat_numbers:
                    seat, created = Seat.objects.get_or_create(
                        room=room,
                        seat_number=seat_num,
                        defaults={'is_available': True}
                    )
                    if created:
                        created_count += 1

                msg = f"Đã tạo tự động thành công {created_count} ghế mới cho phòng '{room.name}'!"
                self.message_user(request, msg, messages.SUCCESS)
                return JsonResponse({'status': 'success', 'message': msg, 'created_count': created_count})
            except Room.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Phòng chiếu không tồn tại!'}, status=404)
            except Exception as exc:
                return JsonResponse({'status': 'error', 'message': f'Lỗi hệ thống: {str(exc)}'}, status=500)

        return JsonResponse({'status': 'error', 'message': 'Yêu cầu không hợp lệ!'}, status=400)


# -------------------------------------------------------------
# QUẢN LÝ SUẤT CHIẾU (Toàn quyền cho Admin Nhánh theo Rạp)
# -------------------------------------------------------------

class ShowtimeAdminForm(forms.ModelForm):
    class Meta:
        model = Showtime
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean() or {}
        movie = cleaned_data.get('movie')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        # Tự động tính Giờ kết thúc theo Thời lượng phim nếu bỏ trống
        if movie and movie.duration and start_time and not end_time:
            import datetime
            dummy_date = datetime.date(2000, 1, 1)
            dt_start = datetime.datetime.combine(dummy_date, start_time)
            dt_end = dt_start + datetime.timedelta(minutes=movie.duration)
            end_time = dt_end.time()
            cleaned_data['end_time'] = end_time

        showtime = Showtime(
            show_date=cleaned_data.get('show_date'),
            start_time=start_time,
            end_time=end_time,
            movie=movie,
            room=cleaned_data.get('room'),
        )

        try:
            validate_showtime(showtime)
        except ValidationError as exc:
            raise forms.ValidationError(exc.messages)

        return cleaned_data


@admin.register(Showtime)
class ShowtimeAdmin(admin.ModelAdmin):
    list_per_page = 20
    form = ShowtimeAdminForm
    autocomplete_fields = ['movie', 'room']
    list_display = (
        'id',
        'get_movie_title',
        'get_cinema_name',
        'room',
        'show_date',
        'get_time_formatted',
        'get_duration_badge',
        'view_detail'
    )
    list_filter = (
        'show_date',
        'room__cinema',
        'movie',
        'room__format',
        'room',
        'created_at'
    )
    search_fields = ('movie__movie_name', 'room__name', 'room__cinema__name')
    ordering = ('-show_date', '-start_time')

    @admin.display(description='Phim chiếu')
    def get_movie_title(self, obj):
        if obj.movie:
            return format_html('<span style="font-weight: 700; color: #ffffff;">{}</span>', obj.movie.movie_name)
        return "-"

    @admin.display(description='Rạp chiếu')
    def get_cinema_name(self, obj):
        if obj.room and obj.room.cinema:
            return format_html('<span style="background: rgba(139, 92, 246, 0.2); color: #c084fc; border: 1px solid rgba(192, 132, 252, 0.4); padding: 3px 10px; border-radius: 12px; font-weight: 700; font-size: 0.8rem;">📍 {}</span>', obj.room.cinema.name)
        return "-"

    @admin.display(description='Khung giờ chiếu')
    def get_time_formatted(self, obj):
        if obj.start_time and obj.end_time:
            start_str = obj.start_time.strftime('%H:%M')
            end_str = obj.end_time.strftime('%H:%M')
            return format_html('<span style="background: rgba(225, 29, 72, 0.15); color: #fb7185; border: 1px solid rgba(251, 113, 133, 0.3); padding: 3px 10px; border-radius: 8px; font-weight: 700; font-size: 0.85rem;">⏰ {} ➔ {}</span>', start_str, end_str)
        return "-"

    @admin.display(description='Thời lượng phim')
    def get_duration_badge(self, obj):
        if obj.movie and obj.movie.duration:
            return format_html('<span style="background: rgba(234, 179, 8, 0.15); color: #facc15; border: 1px solid rgba(250, 204, 21, 0.3); padding: 3px 10px; border-radius: 8px; font-weight: 700; font-size: 0.8rem;">⏱️ {} phút</span>', obj.movie.duration)
        return "-"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if is_branch_admin(request.user):
            cinema = get_user_cinema(request.user)
            return qs.filter(room__cinema=cinema)
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "room" and is_branch_admin(request.user):
            cinema = get_user_cinema(request.user)
            kwargs["queryset"] = Room.objects.filter(cinema=cinema)
        if db_field.name == "movie":
            kwargs["queryset"] = Movie.objects.filter(active=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if is_branch_admin(request.user):
            cinema = get_user_cinema(request.user)
            if obj.room and obj.room.cinema != cinema:
                raise ValidationError("Bạn chỉ có quyền tạo/sửa suất chiếu cho các phòng thuộc rạp mình phụ trách!")
        super().save_model(request, obj, form, change)

    def has_delete_permission(self, request, obj=None):
        if obj is not None and check_showtime_has_sold_seats(obj):
            return False
        return super().has_delete_permission(request, obj)

    def delete_model(self, request, obj):
        try:
            validate_showtime_deletion(obj)
            super().delete_model(request, obj)
        except ValidationError as e:
            messages.error(request, f"Không thể xóa suất chiếu #{obj.id}: {e.message if hasattr(e, 'message') else str(e)}")

    def delete_queryset(self, request, queryset):
        cannot_delete = []
        deleted_count = 0
        for obj in queryset:
            try:
                validate_showtime_deletion(obj)
                obj.delete()
                deleted_count += 1
            except ValidationError:
                cannot_delete.append(f"#{obj.id}")

        if cannot_delete:
            messages.error(
                request,
                f"Không thể xóa {len(cannot_delete)} suất chiếu ({', '.join(cannot_delete)}) vì đã có ít nhất 1 ghế được bán vé!"
            )
        if deleted_count > 0:
            messages.success(request, f"Đã xóa thành công {deleted_count} suất chiếu.")

    @admin.display(description='Thao tác')
    def view_detail(self, obj):
        url = f"/admin/CinemaBook/showtime/{obj.id}/change/"
        return format_html(
            '<a href="{}" style="background: linear-gradient(135deg, #e11d48, #be123c); color: #ffffff; padding: 5px 14px; border-radius: 8px; font-weight: 700; font-size: 0.8rem; text-decoration: none; display: inline-flex; align-items: center; box-shadow: 0 4px 10px rgba(225, 29, 72, 0.35);">Xem chi tiết</a>',
            url
        )



# -------------------------------------------------------------
# QUẢN LÝ TÀI KHOẢN NGƯỜI DÙNG (Superadmin xem & sửa)
# -------------------------------------------------------------

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name = 'Thông tin Vai trò & Rạp quản lý'
    verbose_name_plural = 'Thông tin Vai trò & Rạp quản lý (Profile)'
    fields = ('role', 'cinema', 'name', 'number_phone', 'avatar')


try:
    admin.site.unregister(DjangoUser)
except Exception:
    pass


@admin.register(DjangoUser)
class CustomUserAdmin(BaseUserAdmin):
    list_per_page = 20
    inlines = (UserProfileInline,)
    list_display = ('id', 'get_avatar_preview', 'username', 'email', 'first_name', 'get_role_badge', 'get_cinema', 'is_staff', 'is_active', 'view_detail')
    list_filter = ('profile__role', 'profile__cinema', 'is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'profile__name', 'profile__number_phone')
    ordering = ('username',)

    def has_module_permission(self, request):
        if is_branch_admin(request.user):
            return False
        return super().has_module_permission(request)

    @admin.display(description='Ảnh đại diện')
    def get_avatar_preview(self, obj):
        if hasattr(obj, 'profile') and obj.profile.avatar:
            return format_html(
                '<img src="{}" width="38" height="38" style="object-fit:cover; border-radius:50%; border:2px solid rgba(255,255,255,0.2); box-shadow:0 2px 8px rgba(0,0,0,0.3);" />',
                obj.profile.avatar.url
            )
        return mark_safe('<span style="font-size: 1.2rem; opacity: 0.6;">👤</span>')

    @admin.display(description='Vai trò (Role)')
    def get_role_badge(self, obj):
        if hasattr(obj, 'profile'):
            role_map = {
                'ROLE_ADMIN': ('#ef4444', 'rgba(239, 68, 68, 0.15)', 'Quản trị viên (Admin)'),
                'ROLE_CINEMA_MANAGER': ('#c084fc', 'rgba(192, 132, 252, 0.15)', 'Quản lý Rạp (Admin Nhánh)'),
                'ROLE_STAFF': ('#f59e0b', 'rgba(245, 158, 11, 0.15)', 'Nhân viên (Staff)'),
                'ROLE_USER': ('#3b82f6', 'rgba(59, 130, 246, 0.15)', 'Khách hàng (User)'),
            }
            color, bg, label = role_map.get(obj.profile.role, ('#a1a1aa', 'rgba(161, 161, 170, 0.15)', obj.profile.get_role_display()))
            return format_html(
                '<span style="background: {}; color: {}; border: 1px solid {}; padding: 4px 12px; border-radius: 20px; font-weight: 700; font-size: 0.8rem; display: inline-block;">{}</span>',
                bg, color, color, label
            )
        return "-"

    @admin.display(description='Rạp / Chi nhánh phụ trách')
    def get_cinema(self, obj):
        if hasattr(obj, 'profile') and obj.profile.cinema:
            return obj.profile.cinema.name
        return "-"

    @admin.display(description='Thao tác')
    def view_detail(self, obj):
        url = f"/admin/auth/user/{obj.id}/change/"
        return format_html(
            '<a href="{}" style="background: linear-gradient(135deg, #e11d48, #be123c); color: #ffffff; padding: 5px 14px; border-radius: 8px; font-weight: 700; font-size: 0.8rem; text-decoration: none; display: inline-flex; align-items: center; box-shadow: 0 4px 10px rgba(225, 29, 72, 0.35);">Xem chi tiết</a>',
            url
        )



@admin.register(SeatShowtimeStatus)
class SeatShowtimeStatusAdmin(admin.ModelAdmin):
    list_per_page = 20
    list_display = ('id', 'showtime', 'seat', 'user', 'status', 'lock_time')
    list_filter = ('status', 'showtime__room__cinema', 'showtime__movie', 'showtime__show_date', 'seat__room')
    search_fields = ('seat__seat_number', 'showtime__movie__movie_name', 'user__username')

    def has_module_permission(self, request):
        if is_branch_admin(request.user):
            return False
        return super().has_module_permission(request)


# -------------------------------------------------------------
# QUẢN LÝ LỊCH SỬ ĐẶT VÉ & CHI TIẾT VÉ (Read-only cho Admin Nhánh)
# -------------------------------------------------------------

class TicketInline(admin.TabularInline):
    model = Ticket
    extra = 0
    can_delete = False
    readonly_fields = ('ticket_code', 'seat', 'type_ticket', 'price', 'is_used', 'used_at')

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_per_page = 20
    list_display = (
        'id', 'user', 'get_movie', 'get_showtime_date', 'get_showtime_time',
        'get_seats', 'get_total_price_formatted', 'get_payment_method', 'get_payment_status', 'created_at', 'view_detail'
    )
    list_filter = ('payment_status', 'payment_method', 'showtime__room__cinema', 'showtime__movie', 'showtime__show_date', 'created_at')
    search_fields = ('id', 'user__username', 'user__email', 'user__first_name', 'showtime__movie__movie_name', 'tickets__ticket_code', 'tickets__seat__seat_number')
    ordering = ('-created_at',)
    inlines = [TicketInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if is_branch_admin(request.user):
            cinema = get_user_cinema(request.user)
            return qs.filter(showtime__room__cinema=cinema)
        return qs

    def has_add_permission(self, request):
        if is_branch_admin(request.user):
            return False
        return super().has_add_permission(request)

    def has_change_permission(self, request, obj=None):
        if is_branch_admin(request.user):
            return False
        return super().has_change_permission(request, obj)

    def has_view_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        if is_branch_admin(request.user):
            return False
        return super().has_delete_permission(request, obj)

    @admin.display(description='Thao tác')
    def view_detail(self, obj):
        url = f"/admin/CinemaBook/booking/{obj.id}/change/"
        return format_html(
            '<a href="{}" style="background: linear-gradient(135deg, #e11d48, #be123c); color: #ffffff; padding: 5px 14px; border-radius: 8px; font-weight: 700; font-size: 0.8rem; text-decoration: none; display: inline-flex; align-items: center; box-shadow: 0 4px 10px rgba(225, 29, 72, 0.35);">Xem chi tiết</a>',
            url
        )

    @admin.display(description='Phim')
    def get_movie(self, obj):
        return obj.showtime.movie.movie_name if obj.showtime and obj.showtime.movie else "-"

    @admin.display(description='Ngày chiếu')
    def get_showtime_date(self, obj):
        return obj.showtime.show_date.strftime('%d/%m/%Y') if obj.showtime and obj.showtime.show_date else "-"

    @admin.display(description='Suất chiếu (Giờ)')
    def get_showtime_time(self, obj):
        if obj.showtime and obj.showtime.start_time and obj.showtime.end_time:
            return f"{obj.showtime.start_time.strftime('%H:%M')} - {obj.showtime.end_time.strftime('%H:%M')}"
        return "-"

    @admin.display(description='Chỗ ngồi')
    def get_seats(self, obj):
        seats = [t.seat.seat_number for t in obj.tickets.select_related('seat').all()]
        return ", ".join(seats) if seats else "Chưa chọn ghế"

    @admin.display(description='Tổng tiền')
    def get_total_price_formatted(self, obj):
        price = obj.total_price or 0.0
        formatted = f"{price:,.0f}".replace(",", ".")
        return format_html('<span style="font-weight: 800; color: #f5e625; font-family: monospace;">{} VNĐ</span>', formatted)

    @admin.display(description='Phương thức thanh toán')
    def get_payment_method(self, obj):
        method = (obj.payment_method or '').upper()
        if 'VNPAY' in method or 'ONLINE' in method:
            return format_html('<span style="background: rgba(14, 165, 233, 0.2); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.4); padding: 3px 10px; border-radius: 8px; font-weight: 700; font-size: 0.8rem;">💳 ONLINE VNPAY</span>')
        return format_html('<span style="background: rgba(107, 114, 128, 0.2); color: #9ca3af; border: 1px solid rgba(156, 163, 175, 0.4); padding: 3px 10px; border-radius: 8px; font-weight: 700; font-size: 0.8rem;">💵 Tiền mặt</span>')

    @admin.display(description='Trạng thái thanh toán')
    def get_payment_status(self, obj):
        st = (obj.payment_status or '').upper()
        if st in ('PAID', 'COMPLETED'):
            return format_html('<span style="background: rgba(34, 197, 94, 0.2); color: #4ade80; border: 1px solid rgba(74, 222, 128, 0.4); padding: 4px 12px; border-radius: 20px; font-weight: 800; font-size: 0.8rem;">🟢 ĐÃ THANH TOÁN</span>')
        elif st == 'PENDING':
            return format_html('<span style="background: rgba(234, 179, 8, 0.2); color: #facc15; border: 1px solid rgba(250, 204, 21, 0.4); padding: 4px 12px; border-radius: 20px; font-weight: 800; font-size: 0.8rem;">🟡 CHƯA THANH TOÁN</span>')
        else:
            return format_html('<span style="background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid rgba(248, 113, 113, 0.4); padding: 4px 12px; border-radius: 20px; font-weight: 800; font-size: 0.8rem;">🔴 ĐÃ HỦY</span>')



@admin.register(TypeTicket)
class TypeTicketAdmin(admin.ModelAdmin):
    list_per_page = 20
    list_display = ('id', 'name', 'description', 'get_price_formatted', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('name', 'price', 'created_at')
    ordering = ('-created_at',)

    @admin.display(description='Giá vé')
    def get_price_formatted(self, obj):
        price = obj.price or 0.0
        formatted = f"{price:,.0f}".replace(",", ".")
        return format_html('<span style="font-weight: 700; color: #4ade80; font-family: monospace;">{} VNĐ</span>', formatted)

    def has_module_permission(self, request):
        if is_branch_admin(request.user):
            return False
        return super().has_module_permission(request)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_per_page = 20
    list_display = ('id', 'ticket_code', 'booking', 'seat', 'type_ticket', 'get_price_formatted', 'is_used', 'used_at', 'created_at', 'view_detail')
    list_filter = ('is_used', 'type_ticket', 'booking__payment_status', 'booking__payment_method', 'booking__showtime__room__cinema', 'booking__showtime__movie', 'created_at')
    search_fields = ('ticket_code', 'booking__user__username', 'seat__seat_number', 'type_ticket__name', 'booking__showtime__movie__movie_name')
    ordering = ('-created_at',)

    @admin.display(description='Giá vé')
    def get_price_formatted(self, obj):
        price = obj.price or 0.0
        formatted = f"{price:,.0f}".replace(",", ".")
        return format_html('<span style="font-weight: 700; color: #4ade80; font-family: monospace;">{} VNĐ</span>', formatted)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if is_branch_admin(request.user):
            cinema = get_user_cinema(request.user)
            return qs.filter(booking__showtime__room__cinema=cinema)
        return qs

    def has_add_permission(self, request):
        if is_branch_admin(request.user):
            return False
        return super().has_add_permission(request)

    def has_change_permission(self, request, obj=None):
        if is_branch_admin(request.user):
            return False
        return super().has_change_permission(request, obj)

    def has_view_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        if is_branch_admin(request.user):
            return False
        return super().has_delete_permission(request, obj)

    @admin.display(description='Thao tác')
    def view_detail(self, obj):
        url = f"/admin/CinemaBook/ticket/{obj.id}/change/"
        return format_html(
            '<a href="{}" style="background: linear-gradient(135deg, #e11d48, #be123c); color: #ffffff; padding: 5px 14px; border-radius: 8px; font-weight: 700; font-size: 0.8rem; text-decoration: none; display: inline-flex; align-items: center; box-shadow: 0 4px 10px rgba(225, 29, 72, 0.35);">Xem chi tiết</a>',
            url
        )