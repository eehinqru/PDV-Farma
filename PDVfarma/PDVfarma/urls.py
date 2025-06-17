from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/login/', permanent=False)),
    path('', include('index.urls')),
    path('estoque/', include('estoque.urls')),
    path('', include(('login.urls', 'login'), namespace='login')),
    path('vendas/', include('vendas.urls')),
    path('funcionarios/', include('funcionario.urls')),  
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

