from django.apps import AppConfig


class CinemabookConfig(AppConfig):
    name = 'CinemaBook'

    def ready(self):
        from django.db.models.signals import post_migrate
        post_migrate.connect(create_default_superuser, sender=self)


def create_default_superuser(sender, **kwargs):
    from django.contrib.auth.models import User
    from CinemaBook.models import UserProfile, UserRole

    try:
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@cinebook.vn',
                password='admin123',
                first_name='Quản Trị Viên'
            )
            profile, _ = UserProfile.objects.get_or_create(user=admin_user)
            profile.role = UserRole.ADMIN
            profile.name = 'Quản Trị Viên'
            profile.save()
            print("[AUTO-DEPLOY] Da khoi tao tai khoan Superadmin: admin / admin123")
        else:
            admin_user = User.objects.get(username='admin')
            admin_user.set_password('admin123')
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.save()
            profile, _ = UserProfile.objects.get_or_create(user=admin_user)
            profile.role = UserRole.ADMIN
            profile.save()
            print("[AUTO-DEPLOY] Da cap nhat mat khau Superadmin admin -> admin123")
    except Exception as e:
        print(f"[AUTO-DEPLOY] Warning creating superuser: {e}")

