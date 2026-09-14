from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import auth_views

router = DefaultRouter()
router.register(r'movies', views.MovieViewSet, basename='movie')
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'movie-formats', views.MovieFormatViewSet, basename='movie-format')
router.register(r'cinemas', views.CinemaViewSet, basename='cinema')
router.register(r'showtimes', views.ShowtimeViewSet, basename='showtime')
router.register(r'seats', views.SeatViewSet, basename='seat')
router.register(r'seat-statuses', views.SeatShowtimeStatusViewSet, basename='seat-status')
router.register(r'type-tickets', views.TypeTicketViewSet, basename='type-ticket')
router.register(r'bookings', views.BookingViewSet, basename='booking')
router.register(r'orders', views.BookingViewSet, basename='order')
router.register(r'tickets', views.TicketViewSet, basename='ticket')
router.register(r'profiles', views.ProfileViewSet, basename='profile')

urlpatterns = [
    path('', include(router.urls)),
    path('payments/vnpay-return/', views.vnpay_return_view, name='vnpay_return'),
    path('payments/vnpay-return', views.vnpay_return_view, name='vnpay_return_alt'),
    path('users/', auth_views.RegisterAPIView.as_view(), name='register_user'),
    path('users', auth_views.RegisterAPIView.as_view(), name='register_user_alt'),
    path('login/', auth_views.LoginAPIView.as_view(), name='login_user'),
    path('login', auth_views.LoginAPIView.as_view(), name='login_user_alt'),
    path('auth/google-login/', auth_views.GoogleLoginAPIView.as_view(), name='google_login'),
    path('auth/google/', auth_views.GoogleLoginAPIView.as_view(), name='google_login_alt'),
]

