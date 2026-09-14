from django.contrib.auth.models import User

from rest_framework import status, permissions, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import UserProfile
from ..serializers import ProfileSerializer, UserAuthSerializer


def get_authenticated_user(request):
    if hasattr(request, 'user') and request.user and request.user.is_authenticated:
        return request.user

    auth_header = request.headers.get('Authorization', '') or request.META.get('HTTP_AUTHORIZATION', '')
    if auth_header.startswith('Bearer '):
        token = auth_header.split('Bearer ')[1].strip()
        if token.startswith('token_user_'):
            try:
                return User.objects.filter(pk=int(token.split('_')[2])).first()
            except (IndexError, ValueError):
                pass

    user_id = request.data.get('user_id') or request.query_params.get('user_id')
    if user_id:
        try:
            return User.objects.filter(pk=int(user_id)).first()
        except (ValueError, TypeError):
            pass

    username = request.data.get('username') or request.query_params.get('username')
    return User.objects.filter(username=username).first() if username else None


class ProfileViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin):
    """API Thông tin tài khoản người dùng"""
    queryset = UserProfile.objects.all().select_related('user', 'cinema')
    serializer_class = ProfileSerializer
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=['get'], url_path='current')
    def current_user_profile(self, request):
        user = get_authenticated_user(request)
        if not user:
            return Response({'error': 'Bạn chưa đăng nhập hoặc phiên đăng nhập không hợp lệ!'}, status=status.HTTP_401_UNAUTHORIZED)
        
        UserProfile.objects.get_or_create(user=user)
        return Response(UserAuthSerializer(user, context={'request': request}).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['patch', 'put'], url_path='update-profile')
    def update_profile(self, request):
        user = get_authenticated_user(request)
        if not user:
            return Response({'error': 'Bạn chưa đăng nhập hoặc phiên đăng nhập không hợp lệ!'}, status=status.HTTP_401_UNAUTHORIZED)
        
        profile, _ = UserProfile.objects.get_or_create(user=user)
        data, files = request.data, request.FILES
        
        name = data.get('name') or data.get('first_name')
        email = data.get('email')
        phone = data.get('number_phone') or data.get('phone')
        avatar = files.get('avatar')

        if name is not None:
            profile.name = user.first_name = name.strip()
        if email is not None:
            user.email = email.strip()
        if phone is not None:
            profile.number_phone = phone.strip()
        if avatar:
            profile.avatar = avatar

        user.save()
        profile.save()

        return Response({
            'success': True,
            'message': 'Cập nhật thông tin trang cá nhân thành công!',
            'user': UserAuthSerializer(user, context={'request': request}).data
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='change-password')
    def change_password(self, request):
        user = get_authenticated_user(request)
        if not user:
            return Response({'error': 'Vui lòng đăng nhập để thực hiện đổi mật khẩu!'}, status=status.HTTP_401_UNAUTHORIZED)

        curr_pwd = request.data.get('current_password', '').strip()
        new_pwd = request.data.get('new_password', '').strip()
        cf_pwd = request.data.get('confirm_password', '').strip()

        if not (curr_pwd and new_pwd and cf_pwd):
            return Response({'error': 'Vui lòng điền đầy đủ tất cả các trường mật khẩu!'}, status=status.HTTP_400_BAD_REQUEST)
        if not user.check_password(curr_pwd):
            return Response({'error': 'Mật khẩu hiện tại không chính xác!'}, status=status.HTTP_400_BAD_REQUEST)
        if new_pwd != cf_pwd:
            return Response({'error': 'Mật khẩu mới và mật khẩu xác nhận không trùng khớp!'}, status=status.HTTP_400_BAD_REQUEST)
        if len(new_pwd) < 6:
            return Response({'error': 'Mật khẩu mới phải có ít nhất 6 ký tự!'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_pwd)
        user.save()

        return Response({
            'success': True,
            'message': 'Đổi mật khẩu thành công! Vui lòng dùng mật khẩu mới cho các lần đăng nhập tiếp theo.'
        }, status=status.HTTP_200_OK)
