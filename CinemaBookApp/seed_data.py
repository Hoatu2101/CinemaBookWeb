import os
import sys
import django
from datetime import date, time, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CinemaBookApp.settings')
django.setup()

from django.contrib.auth.models import User
from CinemaBook.models import (
    Category, Status, StatusMovie, MovieFormat, Movie, Cinema, Room, Seat,
    Showtime, TypeTicket, UserProfile, UserRole
)

def seed():
    print("[Seed] Bat dau tao du lieu mau (Seed Data)...")

    # 1. Categories
    cat_names = [
        ("Hành Động", "Phim hành động kịch tính và gay cấn"),
        ("Tình Cảm", "Phim tình cảm lãng mạn lôi cuốn"),
        ("Kinh Dị", "Phim kinh dị rùng rợn, giật gân"),
        ("Hài Hước", "Phim hài hước mang lại tiếng cười sảng khoái"),
        ("Khoa Học Viễn Tưởng", "Phim viễn tưởng kịch tích, công nghệ tương lai"),
        ("Hoạt Hình", "Phim hoạt hình dành cho mọi lứa tuổi")
    ]
    categories = {}
    for name, desc in cat_names:
        c, _ = Category.objects.get_or_create(name=name, defaults={'description': desc})
        categories[name] = c
    print(f"[OK] Da khoi tao {len(categories)} The loai phim.")

    # 2. Status & StatusMovie
    status_active, _ = Status.objects.get_or_create(name="Hoạt động", defaults={'description': "Đang hoạt động bình thường"})
    status_dang_chieu, _ = StatusMovie.objects.get_or_create(name_status="Đang Chiếu")
    status_sap_chieu, _ = StatusMovie.objects.get_or_create(name_status="Sắp Chiếu")

    # 3. MovieFormat
    fmt_2d, _ = MovieFormat.objects.get_or_create(name="2D Standard", defaults={'description': "Định dạng 2D tiêu chuẩn"})
    fmt_3d, _ = MovieFormat.objects.get_or_create(name="3D Digital", defaults={'description': "Định dạng 3D sống động"})
    fmt_imax, _ = MovieFormat.objects.get_or_create(name="IMAX 3D", defaults={'description': "Định dạng màn hình cực đại IMAX"})

    # 4. TypeTicket
    type_normal, _ = TypeTicket.objects.get_or_create(name="Vé Thường", defaults={'price': 75000, 'description': "Vé xem phim ngày thường / cuối tuần"})
    type_vip, _ = TypeTicket.objects.get_or_create(name="Vé VIP", defaults={'price': 95000, 'description': "Vé xem phim ghế trung tâm"})
    type_student, _ = TypeTicket.objects.get_or_create(name="Vé Sinh Viên", defaults={'price': 55000, 'description': "Vé ưu đãi học sinh sinh viên"})
    print("[OK] Da khoi tao cac Loai ve.")

    # 5. Cinema & Room & Seats
    cinema1, _ = Cinema.objects.get_or_create(name="CineBook Landmark 81", defaults={'location': "720A Điện Biên Phủ, Phường 22, Bình Thạnh, TP.HCM"})
    cinema2, _ = Cinema.objects.get_or_create(name="CineBook Thủ Đức", defaults={'location': "216 Võ Văn Ngân, Bình Thọ, TP. Thủ Đức, TP.HCM"})

    room1, _ = Room.objects.get_or_create(name="Phòng Chiếu 01", cinema=cinema1, defaults={'capacity': 20, 'format': fmt_2d, 'status': status_active})
    room2, _ = Room.objects.get_or_create(name="Phòng IMAX", cinema=cinema1, defaults={'capacity': 20, 'format': fmt_imax, 'status': status_active})
    room3, _ = Room.objects.get_or_create(name="Phòng Chiếu A", cinema=cinema2, defaults={'capacity': 20, 'format': fmt_2d, 'status': status_active})

    rooms = [room1, room2, room3]
    rows = ["A", "B", "C", "D"]
    total_seats_created = 0

    for room in rooms:
        for r in rows:
            for num in range(1, 6):
                seat_num = f"{r}{num}"
                s, created = Seat.objects.get_or_create(room=room, seat_number=seat_num, defaults={'is_available': True})
                if created:
                    total_seats_created += 1

    print(f"[OK] Da khoi tao Rap, Phong chieu va {total_seats_created} Ghe ngoi.")

    # 6. Movies
    sample_movies = [
        {
            "movie_name": "Avatar: Dòng Chảy Của Nước",
            "description": "Câu chuyện tiếp theo về gia đình Sully khi họ phải rời bỏ quê hương Pandora để khám phá những vùng biển mới và đối mặt với hiểm nguy.",
            "duration": 192,
            "release_year": 2022,
            "actor": "Sam Worthington, Zoe Saldana",
            "drirector": "James Cameron",
            "status_movie": status_dang_chieu,
            "poster": "posters/avatar.jpg",
            "cates": ["Hành Động", "Khoa Học Viễn Tưởng"]
        },
        {
            "movie_name": "Mai",
            "description": "Bộ phim tâm lý tình cảm xoay quanh cuộc đời của Mai - một người phụ nữ massage với những ước mơ và góc khuất cuộc sống.",
            "duration": 131,
            "release_year": 2024,
            "actor": "Phương Anh Đào, Tuấn Trần",
            "drirector": "Trấn Thành",
            "status_movie": status_dang_chieu,
            "poster": "posters/mai.jpg",
            "cates": ["Tình Cảm", "Hài Hước"]
        },
        {
            "movie_name": "Lật Mặt 7: Một Điều Ước",
            "description": "Câu chuyện tình cảm gia đình cảm động về người mẹ đơn thân và 5 người con với những hoàn cảnh cuộc sống khác nhau.",
            "duration": 138,
            "release_year": 2024,
            "actor": "Thanh Hiền, Trương Minh Cường, Đinh Y Nhung",
            "drirector": "Lý Hải",
            "status_movie": status_dang_chieu,
            "poster": "posters/latmat7.jpg",
            "cates": ["Tình Cảm", "Hài Hước"]
        },
        {
            "movie_name": "Dune: Hành Tinh Cát 2",
            "description": "Paul Atreides hội ngộ với Chani và người Fremen trên hành trình trả thù những kẻ đã hủy hoại gia đình anh.",
            "duration": 166,
            "release_year": 2024,
            "actor": "Timothée Chalamet, Zendaya",
            "drirector": "Denis Villeneuve",
            "status_movie": status_dang_chieu,
            "poster": "posters/dune2.jpg",
            "cates": ["Khoa Học Viễn Tưởng", "Hành Động"]
        },
        {
            "movie_name": "Kung Fu Panda 4",
            "description": "Po trở thành Thủ Lĩnh Tinh Thần của Thung Lũng Bình Yên và phải tìm kiếm một Thần Long Đại Hiệp mới.",
            "duration": 94,
            "release_year": 2024,
            "actor": "Jack Black, Awkwafina",
            "drirector": "Mike Mitchell",
            "status_movie": status_sap_chieu,
            "poster": "posters/kungfupanda4.jpg",
            "cates": ["Hoạt Hình", "Hài Hước"]
        }
    ]

    created_movies = []
    for m_data in sample_movies:
        cates = m_data.pop("cates")
        movie, _ = Movie.objects.get_or_create(
            movie_name=m_data["movie_name"],
            defaults=m_data
        )
        for c_name in cates:
            if c_name in categories:
                movie.categories.add(categories[c_name])
        created_movies.append(movie)

    print(f"[OK] Da khoi tao {len(created_movies)} Bo phim mau.")

    # 7. Showtimes
    today = date.today()
    time_slots = [
        (time(9, 30), time(11, 30)),
        (time(13, 0), time(15, 0)),
        (time(16, 30), time(18, 30)),
        (time(19, 45), time(21, 45)),
    ]

    showtime_count = 0
    for day_offset in range(0, 5):
        st_date = today + timedelta(days=day_offset)
        for idx, movie in enumerate(created_movies):
            room = rooms[idx % len(rooms)]
            start_t, end_t = time_slots[idx % len(time_slots)]
            
            st, created = Showtime.objects.get_or_create(
                movie=movie,
                room=room,
                show_date=st_date,
                start_time=start_t,
                defaults={'end_time': end_t}
            )
            if created:
                showtime_count += 1

    print(f"[OK] Da khoi tao {showtime_count} Suat chieu cho cac ngay toi.")

    # 8. User Accounts (Khách hàng, Nhân viên, Admin)
    user_kh, created_kh = User.objects.get_or_create(
        username="khachhang",
        defaults={'first_name': "Nguyễn Văn Khách", 'email': "khachhang@gmail.com", 'is_staff': False, 'is_superuser': False}
    )
    if created_kh:
        user_kh.set_password("123456")
        user_kh.save()
    p_kh, _ = UserProfile.objects.get_or_create(user=user_kh)
    p_kh.role = UserRole.USER
    p_kh.name = "Nguyễn Văn Khách"
    p_kh.number_phone = "0901234567"
    p_kh.save()

    user_staff, created_staff = User.objects.get_or_create(
        username="nhanvien",
        defaults={'first_name': "Lê Nhân Viên", 'email': "nhanvien@cinebook.vn", 'is_staff': True, 'is_superuser': False}
    )
    if created_staff:
        user_staff.set_password("123456")
        user_staff.save()
    p_staff, _ = UserProfile.objects.get_or_create(user=user_staff)
    p_staff.role = UserRole.STAFF
    p_staff.name = "Lê Nhân Viên"
    p_staff.cinema = cinema1
    p_staff.number_phone = "0987654321"
    p_staff.save()

    user_admin, created_admin = User.objects.get_or_create(
        username="admin",
        defaults={'first_name': "Quản Trị Viên", 'email': "admin@cinebook.vn", 'is_staff': True, 'is_superuser': True}
    )
    if created_admin:
        user_admin.set_password("admin123")
        user_admin.save()
    p_admin, _ = UserProfile.objects.get_or_create(user=user_admin)
    p_admin.role = UserRole.ADMIN
    p_admin.name = "Quản Trị Viên"
    p_admin.save()

    print("[OK] Da khoi tao cac tai khoan mau:")
    print("   Khach hang : Username='khachhang', Password='123456' (Role: ROLE_USER)")
    print("   Nhan vien  : Username='nhanvien', Password='123456' (Role: ROLE_STAFF)")
    print("   Admin      : Username='admin', Password='admin123' (Role: ROLE_ADMIN)")
    print("\n[SUCCESS] HOAN THANH TAO DU LIEU MAU!")

if __name__ == "__main__":
    seed()
