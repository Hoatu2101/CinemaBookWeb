"""
CinemaBook Application Views
----------------------------
File này đóng vai trò tập hợp (re-export) tất cả các API ViewSets & Views
được tổ chức theo dạng module nhỏ nằm trong gói `CinemaBook.viewAPI`.

Cấu trúc các module trong `viewAPI/`:
  - `movie_views.py`: MovieViewSet, CategoryViewSet, MovieFormatViewSet, CinemaViewSet, MovieListApi, CategoryListApi
  - `showtime_views.py`: ShowtimeViewSet
  - `seat_views.py`: SeatViewSet, SeatShowtimeStatusViewSet
  - `booking_views.py`: TypeTicketViewSet, BookingViewSet, TicketViewSet
  - `staff_views.py`: is_staff_member, staff_check_ticket_view, staff_verify_ticket_api
  - `profile_views.py`: get_authenticated_user, ProfileViewSet
  - `payment_views.py`: index, revenue_stats_view, vnpay_return_view
  - `gemini_views.py`: gemini_generate_description_api, gemini_chat_api, gemini_analyze_revenue_api
"""

from .viewAPI.movie_views import (
    MovieViewSet,
    CategoryViewSet,
    MovieFormatViewSet,
    CinemaViewSet,
    MovieListApi,
    CategoryListApi,
)

from .viewAPI.showtime_views import (
    ShowtimeViewSet,
)

from .viewAPI.seat_views import (
    SeatViewSet,
    SeatShowtimeStatusViewSet,
)

from .viewAPI.booking_views import (
    TypeTicketViewSet,
    BookingViewSet,
    TicketViewSet,
)

from .viewAPI.staff_views import (
    is_staff_member,
    staff_check_ticket_view,
    staff_verify_ticket_api,
    staff_register_view,
)

from .viewAPI.profile_views import (
    get_authenticated_user,
    ProfileViewSet,
)

from .viewAPI.payment_views import (
    index,
    revenue_stats_view,
    vnpay_return_view,
)

from .viewAPI.gemini_views import (
    gemini_generate_description_api,
    gemini_chat_api,
    gemini_analyze_revenue_api,
)

__all__ = [
    # Movie APIs
    'MovieViewSet',
    'CategoryViewSet',
    'MovieFormatViewSet',
    'CinemaViewSet',
    'MovieListApi',
    'CategoryListApi',

    # Showtime & Seat APIs
    'ShowtimeViewSet',
    'SeatViewSet',
    'SeatShowtimeStatusViewSet',

    # Booking & Ticket APIs
    'TypeTicketViewSet',
    'BookingViewSet',
    'TicketViewSet',

    # Staff Views
    'is_staff_member',
    'staff_check_ticket_view',
    'staff_verify_ticket_api',
    'staff_register_view',

    # Profile APIs
    'get_authenticated_user',
    'ProfileViewSet',

    # Payment & Stats Views
    'index',
    'revenue_stats_view',
    'vnpay_return_view',

    # Gemini AI Views
    'gemini_generate_description_api',
    'gemini_chat_api',
    'gemini_analyze_revenue_api',
]