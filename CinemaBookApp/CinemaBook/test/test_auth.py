from unittest.mock import patch
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from CinemaBook.models import UserProfile, UserRole
from CinemaBook.viewAPI.staff_views import is_staff_member


class GoogleLoginTestCase(APITestCase):
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.url = reverse('google_login')

    def test_google_login_get(self):
        """Test GET request to Google Login API returns instructions (200 OK)"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        resp_data = getattr(response, 'data', {})
        self.assertIn('message', resp_data)
        self.assertIn('example_request_body', resp_data)

    def test_google_login_post_invalid_data(self):
        """Test POST request with missing id_token returns 400 Bad Request"""
        response = self.client.post(self.url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        resp_data = getattr(response, 'data', {})
        self.assertIn('error', resp_data)

    @patch('CinemaBook.auth_views.requests.get')
    def test_google_login_post_valid_mock_token(self, mock_requests_get):
        """Test POST request with valid mock Google Token creates User & UserProfile"""
        mock_payload = {
            'email': 'unittestuser@gmail.com',
            'given_name': 'Test',
            'family_name': 'User',
            'sub': '1234567890'
        }
        mock_requests_get.return_value.status_code = 200
        mock_requests_get.return_value.json.return_value = mock_payload

        response = self.client.post(self.url, {'id_token': 'valid_mock_id_token'}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        resp_data = getattr(response, 'data', {})
        self.assertTrue(resp_data.get('success'))
        self.assertEqual(resp_data['user']['email'], 'unittestuser@gmail.com')

        user = User.objects.filter(email='unittestuser@gmail.com').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.first_name, 'Test')

        profile, _ = UserProfile.objects.get_or_create(user=user)
        self.assertIsNotNone(profile)


class StaffMemberCheckTestCase(TestCase):
    def setUp(self):
        self.normal_user = User.objects.create_user(
            username='normal_user',
            email='normal@example.com',
            password='password123'
        )
        self.staff_user = User.objects.create_user(
            username='staff_user',
            email='staff@example.com',
            password='password123'
        )
        UserProfile.objects.get_or_create(user=self.normal_user)
        staff_profile, _ = UserProfile.objects.get_or_create(user=self.staff_user)
        staff_profile.role = UserRole.STAFF
        staff_profile.save()

    def test_is_staff_member_normal_user(self):
        """Test normal user is not recognized as staff"""
        self.normal_user.refresh_from_db()
        self.assertFalse(is_staff_member(self.normal_user))

    def test_is_staff_member_staff_user(self):
        """Test user with profile role ROLE_STAFF is recognized as staff"""
        self.staff_user.refresh_from_db()
        self.assertTrue(is_staff_member(self.staff_user))

    def test_is_staff_member_role_staff(self):
        """Test user with profile role ROLE_STAFF is recognized as staff"""
        profile, _ = UserProfile.objects.get_or_create(user=self.normal_user)
        profile.role = UserRole.STAFF
        profile.save()
        self.normal_user.refresh_from_db()
        self.assertTrue(is_staff_member(self.normal_user))


class ProfileAPITestCase(APITestCase):
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.user = User.objects.create_user(username='testprofile', email='profile@test.com', password='oldpassword123')
        UserProfile.objects.get_or_create(user=self.user)

        self.current_profile_url = reverse('profile-current-user-profile')
        self.update_profile_url = reverse('profile-update-profile')
        self.change_password_url = reverse('profile-change-password')

    def test_get_current_profile_authenticated(self):
        """Test lấy thông tin trang cá nhân người dùng hiện tại -> HTTP 200 OK"""
        getattr(self.client, 'force_authenticate')(user=self.user)
        response = self.client.get(self.current_profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        resp_data = getattr(response, 'data', {})
        self.assertEqual(resp_data['email'], 'profile@test.com')

    def test_change_password_success(self):
        """Test đổi mật khẩu thành công -> HTTP 200 OK & mật khẩu mới hoạt động"""
        getattr(self.client, 'force_authenticate')(user=self.user)
        payload = {
            'current_password': 'oldpassword123',
            'new_password': 'newpassword456',
            'confirm_password': 'newpassword456'
        }
        response = self.client.post(self.change_password_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword456'))

    def test_update_profile_success(self):
        """Test cập nhật thông tin trang cá nhân -> HTTP 200 OK & lưu DB thành công"""
        getattr(self.client, 'force_authenticate')(user=self.user)
        payload = {
            'name': 'Nguyễn Văn Test',
            'email': 'newemail@test.com',
            'number_phone': '0987654321'
        }
        response = self.client.patch(self.update_profile_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        resp_data = getattr(response, 'data', {})
        self.assertTrue(resp_data.get('success'))

        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'newemail@test.com')
        self.assertEqual(self.user.profile.name, 'Nguyễn Văn Test')
        self.assertEqual(self.user.profile.number_phone, '0987654321')

    def test_change_password_wrong_current_password(self):
        """Test đổi mật khẩu với mật khẩu hiện tại sai -> HTTP 400 Bad Request"""
        getattr(self.client, 'force_authenticate')(user=self.user)
        payload = {
            'current_password': 'wrongpassword',
            'new_password': 'newpassword456',
            'confirm_password': 'newpassword456'
        }
        response = self.client.post(self.change_password_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        resp_data = getattr(response, 'data', {})
        self.assertIn('error', resp_data)

    def test_change_password_mismatch(self):
        """Test đổi mật khẩu với mật khẩu xác nhận không khớp -> HTTP 400 Bad Request"""
        getattr(self.client, 'force_authenticate')(user=self.user)
        payload = {
            'current_password': 'oldpassword123',
            'new_password': 'newpassword456',
            'confirm_password': 'mismatchedpassword'
        }
        response = self.client.post(self.change_password_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        resp_data = getattr(response, 'data', {})
        self.assertIn('error', resp_data)

    def test_unauthenticated_profile_access(self):
        """Test chưa đăng nhập truy cập profile -> HTTP 401 Unauthorized"""
        response = self.client.get(self.current_profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
