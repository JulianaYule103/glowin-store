from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from usuarios.views import home

urlpatterns = [
    path('', home, name='home'),
    
    path('admin/', admin.site.urls),

    # Home y usuarios
    path('', include('usuarios.urls')),

    # Productos (catálogo)
    path('productos/', include('productos.urls')),

    # Login / Registro
    path('accounts/', include('allauth.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
