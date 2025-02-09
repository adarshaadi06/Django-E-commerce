from django.contrib import admin
from django.urls import path, include
from django.conf import settings

from django.conf.urls.static import static

from store import views as store_views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('admin/', admin.site.urls),
    # API endpoints (with a namespace "api")
    path('api/', include(('store.api_urls', 'api'))),
    # Frontend endpoints (with a namespace "store")
    path('', include(('store.urls', 'store'))),
    # Authentication URLs for regular users
    path('signup/', store_views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='store/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='store:home'), name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)