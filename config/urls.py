# config/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from core.views import CustomLoginView
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

# Dilə həssas olan URL-lər
i18n_urlpatterns = i18n_patterns(
    path('accounts/login/', CustomLoginView.as_view(), name='login'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('core.urls')),
)

# Dilə həssas olmayan URL-lər
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('core.api_urls')),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
urlpatterns += i18n_urlpatterns

# --- STATİK FAYLLAR ÜÇün URL KONFİQURASİYASI ---
# Yalnız DEVELOPMENT rejimində (DEBUG=True) statik və media faylları üçün URL-lər
if settings.DEBUG:
    # Static faylları serve et (STATIC_ROOT-dan)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # İstifadəçilərin yüklədiyi şəkilləri və faylları serve et
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# Xəta handler-ləri
handler400 = 'django.views.defaults.bad_request'
handler403 = 'django.views.defaults.permission_denied'
handler404 = 'django.views.defaults.page_not_found'
handler500 = 'django.views.defaults.server_error'