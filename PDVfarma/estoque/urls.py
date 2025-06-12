from django.urls import path
from . import views


urlpatterns = [
    path('', views.estoque, name='estoque'),
    path('listar/', views.listar_produtos, name='listar_produtos'),
    path('criar/', views.criar_produto, name='criar_produto'),
    path('atualizar/<int:id>/', views.atualizar_produto, name='atualizar_produto'),
    path('deletar/<int:produto_id>/', views.deletar_produto, name='deletar_produto'),
    path('dashboard/', views.dashboard, name='dashboard'),
]
