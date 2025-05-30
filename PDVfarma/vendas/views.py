# views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.decorators import login_required
from .models import Produto, Venda, ItemVenda

@login_required
@transaction.atomic
def nova_venda(request):
    if request.method == 'POST':
        itens = []
        total = 0

        for i in range(0, int(request.POST.get('total_itens', 0))):
            produto_id = request.POST.get(f'produto_{i}')
            quantidade = int(request.POST.get(f'quantidade_{i}', 0))

            if produto_id and quantidade > 0:
                produto = Produto.objects.get(id=produto_id)
                preco = produto.preco
                subtotal = preco * quantidade
                total += subtotal
                itens.append({
                    'produto': produto,
                    'quantidade': quantidade,
                    'preco': preco,
                    'subtotal': subtotal,
                })

        valor_recebido = float(request.POST.get('valor_recebido', 0))
        troco = valor_recebido - total

        if troco < 0:
            messages.error(request, "Valor recebido é insuficiente.")
            return redirect('nova_venda')

        # Cria a venda e os itens
        venda = Venda.objects.create(
            funcionario=request.user,
            total=total,
            valor_recebido=valor_recebido,
            troco=troco
        )

        for item in itens:
            ItemVenda.objects.create(
                venda=venda,
                produto=item['produto'],
                quantidade=item['quantidade'],
                preco_unitario=item['preco'],
                subtotal=item['subtotal']
            )

        messages.success(request, "Venda registrada com sucesso.")
        return redirect('historico_vendas')

    produtos = Produto.objects.all()
    return render(request, 'vendas/nova_venda.html', {'produtos': produtos})

@login_required
def historico_vendas(request):
    vendas = Venda.objects.select_related('funcionario').prefetch_related('itens__produto').order_by('-data')
    return render(request, 'vendas/historico.html', {'vendas': vendas})