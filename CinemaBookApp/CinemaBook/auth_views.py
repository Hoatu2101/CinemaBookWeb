import requests
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.db import transaction
from django.utils.crypto import get_random_string
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import UserProfile, UserRole
from .serializers import GoogleLoginSerializer, UserAuthSerializer

try:
    from google.oauth2 import id_token as google_id_token
    from google.auth.transport import requests as google_requests
    GOOGLE_AUTH_AVAILABLE = True
except ImportError:
    GOOGLE_AUTH_AVAILABLE = False


class RegisterAPIView(APIView):
    """
    API Đăng ký tài khoản người dùng mới (chỉ nhận POST)
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        data = request.data
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        name = data.get('name', '').strip()
        number_phone = data.get('number_phone', '').strip()
        avatar = request.FILES.get('avatar')

        if not username or not password:
            return Response({'error': 'Tên đăng nhập và mật khẩu là bắt buộc!'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({'error': 'Tên đăng nhập đã tồn tại trên hệ thống!'}, status=status.HTTP_400_BAD_REQUEST)

        email = data.get('email', '').strip()
        if not email:
            email = username if '@' in username else f"{username}@gmail.com"

        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=name,
                    is_staff=False,
                    is_superuser=False
                )

                profile, _ = UserProfile.objects.get_or_create(user=user)
                profile.role = UserRole.USER
                if name:
                    profile.name = name
                if number_phone:
                    profile.number_phone = number_phone
                if avatar:
                    profile.avatar = avatar
                profile.save()

            user_data = UserAuthSerializer(user).data
            return Response({
                'success': True,
                'message': 'Đăng ký tài khoản thành công!',
                'user': user_data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': f'Không thể đăng ký: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LoginAPIView(APIView):
    """
    API Đăng nhập tài khoản (chỉ nhận POST)
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get('username', '').strip()
        password = request.data.get('password', '').strip()

        if not username or not password:
            return Response({'error': 'Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu!'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)
        if not user:
            return Response({'error': 'Tên đăng nhập hoặc mật khẩu không chính xác!'}, status=status.HTTP_400_BAD_REQUEST)

        user_data = UserAuthSerializer(user).data
        token_str = f"token_user_{user.id}_{get_random_string(16)}"
        return Response({
            'token': token_str,
            'user': user_data
        }, status=status.HTTP_200_OK)


class GoogleLoginAPIView(APIView):
    """
    API Đăng nhập / Đăng ký qua Google OAuth2 (Google Sign-In)
    Nhận ID Token từ Google, xác thực và trả về thông tin tài khoản người dùng.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        """Trả về hướng dẫn sử dụng API Đăng nhập Google"""
        return Response({
            'message': 'Api working.',
            'endpoint': '/api/auth/google-login/',
            'method': 'POST',
            'example_request_body': {
                'id_token': 'GOOGLE_ID_TOKEN'
            }
        }, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Đăng nhập / Xác thực Google OAuth2",
        description="Gửi Google ID Token (`id_token`) để xác thực người dùng và đăng nhập vào hệ thống.",
        request=GoogleLoginSerializer,
        responses={
            200: OpenApiResponse(response=UserAuthSerializer, description="Đăng nhập Google thành công"),
            400: OpenApiResponse(description="Token không hợp lệ hoặc thiếu thông tin"),
            500: OpenApiResponse(description="Lỗi hệ thống khi xác thực Google Token")
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = GoogleLoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'error': 'Dữ liệu không hợp lệ', 'details': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        id_token_str = serializer.validated_data.get('id_token')
        payload = None

        # 1. Thử verify bằng google-auth library
        if GOOGLE_AUTH_AVAILABLE:
            try:
                request_adapter = google_requests.Request()
                payload = google_id_token.verify_oauth2_token(id_token_str, request_adapter, clock_skew_in_seconds=10)
            except Exception:
                payload = None

        # 2. Fallback: Verify qua endpoint công khai của Google TokenInfo API
        if not payload:
            try:
                resp = requests.get(f'https://oauth2.googleapis.com/tokeninfo?id_token={id_token_str}', timeout=10)
                if resp.status_code == 200:
                    payload = resp.json()
            except Exception as e:
                return Response({'error': f'Không thể kết nối đến máy chủ Google OAuth: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if not payload or 'email' not in payload:
            return Response({'error': 'Google ID Token không hợp lệ hoặc đã hết hạn!'}, status=status.HTTP_400_BAD_REQUEST)

        email = payload.get('email')
        first_name = payload.get('given_name') or payload.get('name', '').split(' ')[0]
        last_name = payload.get('family_name') or ''
        google_sub = payload.get('sub', '')

        # 3. Tìm người dùng đã tồn tại theo Email hoặc Username
        user = User.objects.filter(email=email).first()

        if not user:
            # Tạo username từ email hoặc google_sub
            base_username = email.split('@')[0] if email else f"google_{google_sub[:8]}"
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}_{counter}"
                counter += 1

            # Tạo user mới với ngẫu nhiên password
            random_password = get_random_string(length=16)
            user = User.objects.create_user(
                username=username,
                email=email,
                password=random_password,
                first_name=first_name,
                last_name=last_name
            )

        # Cập nhật thông tin profile nếu có
        profile, created = UserProfile.objects.get_or_create(user=user)
        if first_name or last_name:
            if not profile.name:
                profile.name = f"{first_name} {last_name}".strip()
                profile.save()

        user_data = UserAuthSerializer(user).data

        return Response({
            'success': True,
            'message': 'Đăng nhập Google thành công!',
            'user': user_data
        }, status=status.HTTP_200_OK)
