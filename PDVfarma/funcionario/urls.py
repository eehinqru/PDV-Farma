from django.urls import path
from . import views

urlpatterns = [
    path('listar/', views.listar_funcionarios, name='listar_funcionarios'),
    path('registrar/', views.registrar_funcionario, name='registrar_funcionario'),
    path('funcionarios/editar/<int:funcionario_id>/', views.editar_funcionario, name='editar_funcionario'),
    path('funcionarios/deletar/<int:funcionario_id>/', views.deletar_funcionario, name='deletar_funcionario'),
]
