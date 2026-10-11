from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

def health(request): return JsonResponse({'status': 'ok'})
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/health/', health),
    path('api/token/', TokenObtainPairView.as_view()),
    path('api/token/refresh/', TokenRefreshView.as_view()),
    path('api/users/', include('apps.users.urls')),
    path('api/', include('apps.content.urls')),
    path('api/', include('apps.inquiries.urls')),
    path('api/', include('apps.seo.urls')),
]

# `runserver` does not serve MEDIA_ROOT on its own, so an uploaded or downloaded
# image would 404 in development. Only while DEBUG is on; a real deploy puts
# these behind the web server.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
