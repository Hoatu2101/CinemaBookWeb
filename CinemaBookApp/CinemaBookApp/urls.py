from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from django.contrib import admin
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from CinemaBook import views

from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(url='/admin/', permanent=False)),

    # OpenAPI Schema & Swagger UI / ReDoc
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui-alt'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    path('admin/revenue-stats/', views.revenue_stats_view, name='revenue_stats'),
    path('admin/staff/register/', views.staff_register_view, name='staff_register'),
    path('admin/staff/check-ticket/', views.staff_check_ticket_view, name='staff_check_ticket'),
    path('admin/staff/api/verify-ticket/', views.staff_verify_ticket_api, name='staff_verify_ticket'),
    path('admin/gemini/generate-description/', views.gemini_generate_description_api, name='gemini_gen_description'),

    path('admin/gemini/chat/', views.gemini_chat_api, name='gemini_chat'),
    path('api/chat/', views.gemini_chat_api, name='api_gemini_chat'),
    path('admin/gemini/analyze-revenue/', views.gemini_analyze_revenue_api, name='gemini_analyze_revenue'),
    path('admin/', admin.site.urls),
    path('api/', include('CinemaBook.urls')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
