from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('index.urls')),
    path('estoque/', include('estoque.urls')),
    path('', include('login.urls')),
    path('vendas/', include('vendas.urls')),
    path('funcionarios/', include('funcionario.urls')),  
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

