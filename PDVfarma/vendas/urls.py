from django.urls import path
from . import views
from django.shortcuts import redirect

def redirect_vendas_root(request):
    return redirect('nova_venda') 

urlpatterns = [
    path('', redirect_vendas_root),  
    path('nova/', views.nova_venda, name='nova_venda'),
    path('historico/', views.historico_vendas, name='historico_vendas'),
]
