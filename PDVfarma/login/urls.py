from django.urls import path
from .views import login_view
from . import views

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]