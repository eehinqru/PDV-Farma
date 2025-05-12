from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group

@login_required
def vendas(request):
    if request.user.groups.filter(name='dono').exists():
        # Redireciona o dono para o estoque
        return redirect('listar_produtos')
    elif request.user.groups.filter(name='funcionario').exists():
        # Redireciona o funcionário para o estoque (ou outra página de vendas que você criar depois)
        return redirect('listar_produtos')
    return render(request, 'vendas/dashboard.html')