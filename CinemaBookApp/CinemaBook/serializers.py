from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Movie, Category, MovieFormat, UserProfile, Cinema, Room, Seat, Showtime,
    SeatShowtimeStatus, Booking, TypeTicket, Ticket
)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class MovieFormatSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovieFormat
        fields = '__all__'


class CinemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cinema
        fields = '__all__'


class MovieSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    poster = serializers.SerializerMethodField()

    class Meta:
        model = Movie
        fields = '__all__'

    def get_poster(self, obj):
        if not obj.poster:
            return "https://res.cloudinary.com/dxxwcby8l/image/upload/v1717013892/Cinemax-Placeholder-Gold-Star_d3k4e0.jpg"
        url = str(obj.poster.url) if hasattr(obj.poster, 'url') else str(obj.poster)
        if url.startswith('http://') or url.startswith('https://'):
            return url
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(url)
        return url


#api profile
class ProfileSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_first_name = serializers.CharField(source='user.first_name', read_only=True)
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = '__all__'

    def get_avatar(self, obj):
        if not obj.avatar:
            return None
        url = str(obj.avatar.url) if hasattr(obj.avatar, 'url') else str(obj.avatar)
        if url.startswith('http://') or url.startswith('https://'):
            return url
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(url)
        return url


#Seriliazer seat 
class SeatSerializer(serializers.ModelSerializer):
    room_name = serializers.CharField(source='room.name', read_only=True)

    class Meta:
        model = Seat
        fields = '__all__'


class SeatShowtimeStatusSerializer(serializers.ModelSerializer):
    seat_number = serializers.CharField(source='seat.seat_number', read_only=True)

    class Meta:
        model = SeatShowtimeStatus
        fields = '__all__'


#Seriliazer showtime
class ShowtimeSerializer(serializers.ModelSerializer):
    movie_name = serializers.CharField(source='movie.movie_name', read_only=True)
    movie_poster = serializers.ImageField(source='movie.poster', read_only=True)
    room_name = serializers.CharField(source='room.name', read_only=True)
    cinema_name = serializers.SerializerMethodField()
    cinema_location = serializers.SerializerMethodField()

    class Meta:
        model = Showtime
        fields = '__all__'

    def get_cinema_name(self, obj):
        if obj.room and obj.room.cinema:
            return obj.room.cinema.name
        return "Rạp CineBook"

    def get_cinema_location(self, obj):
        if obj.room and obj.room.cinema:
            return obj.room.cinema.location
        return ""


#Seriliazer ticket
class TypeTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeTicket
        fields = '__all__'


class TicketSerializer(serializers.ModelSerializer):
    seat_number = serializers.CharField(source='seat.seat_number', read_only=True)
    type_ticket_name = serializers.CharField(source='type_ticket.name', read_only=True)

    class Meta:
        model = Ticket
        fields = '__all__'


#Seriliazer booking
class BookingSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    movie_title = serializers.CharField(source='showtime.movie.movie_name', read_only=True)
    movie_poster = serializers.ImageField(source='showtime.movie.poster', read_only=True)
    cinema_name = serializers.CharField(source='showtime.room.cinema.name', read_only=True)
    room_name = serializers.CharField(source='showtime.room.name', read_only=True)
    showtime_date = serializers.CharField(read_only=True)
    showtime_time = serializers.CharField(read_only=True)

    class Meta:
        model = Booking
        fields = '__all__'


#Seriliazer order
class TicketItemSerializer(serializers.Serializer):
    seat_id = serializers.IntegerField()
    type_ticket_id = serializers.IntegerField(required=False, allow_null=True)


class OrderSerializer(serializers.ModelSerializer):
    """Serializer dành cho việc khởi tạo và xem Đơn hàng (Order)"""
    tickets = TicketSerializer(many=True, read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    movie_title = serializers.CharField(source='showtime.movie.movie_name', read_only=True)
    ticket_items = TicketItemSerializer(many=True, write_only=True, required=False)

    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ['total_price', 'created_at']


class GoogleLoginSerializer(serializers.Serializer):
    id_token = serializers.CharField(
        required=True,
        help_text="Google OAuth2 ID Token từ Google Sign-In SDK"
    )
    access_token = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Google OAuth2 Access Token (tùy chọn)"
    )


class UserAuthSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source='profile.role', read_only=True)
    avatar = serializers.ImageField(source='profile.avatar', read_only=True)
    cinema_id = serializers.IntegerField(source='profile.cinema_id', read_only=True)
    name = serializers.CharField(source='profile.name', read_only=True)
    number_phone = serializers.CharField(source='profile.number_phone', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'role', 'avatar', 'cinema_id', 'name', 'number_phone']