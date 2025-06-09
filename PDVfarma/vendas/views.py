from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.decorators import login_required
from .models import Produto, Venda, ItemVenda
from estoque.models import Lote 
from django.db.models import F
from decimal import Decimal 

@login_required
@transaction.atomic
def nova_venda(request):
    if request.method == 'POST':
        total_itens = int(request.POST.get('total_itens', 0))
        valor_recebido_str = request.POST.get('valor_recebido', '0').replace(',', '.') # Lidar com vírgula como separador decimal
        
        try:
            # <--- Mude float() para Decimal() aqui
            valor_recebido = Decimal(valor_recebido_str) 
        except ValueError:
            messages.error(request, "Por favor, insira um valor recebido válido.")
            produtos = Produto.objects.filter(ativo=True).annotate(
                categoria_display=F('categoria')
            ).values('id', 'nome', 'preco', 'codigo_barras', 'categoria', 'quantidade_estoque')
            for p in produtos:
                p['categoria_display'] = dict(Produto.CATEGORIAS).get(p['categoria'], p['categoria'])
            return render(request, 'vendas/nova_venda.html', {'produtos_data': list(produtos)})


        itens_para_venda = []
        # <--- Mude 0 para Decimal('0.00') aqui
        total_venda = Decimal('0.00') 

        for i in range(total_itens):
            produto_id = request.POST.get(f'produto_{i}')
            quantidade = int(request.POST.get(f'quantidade_{i}', 0))

            if not produto_id or quantidade <= 0:
                messages.error(request, "Dados inválidos para um dos itens da venda.")
                return redirect('nova_venda')

            produto = get_object_or_404(Produto, id=produto_id)
            
            # Validação de estoque:
            if quantidade > produto.quantidade_estoque:
                messages.error(request, f"Quantidade insuficiente para {produto.nome}. Estoque disponível: {produto.quantidade_estoque}")
                return redirect('nova_venda')
            
            # produto.preco já é um Decimal (se o seu campo for DecimalField)
            preco_unitario = produto.preco 
            subtotal = preco_unitario * quantidade # Isso resultará em um Decimal
            total_venda += subtotal # Somando Decimal com Decimal

            itens_para_venda.append({
                'produto': produto,
                'quantidade': quantidade,
                'preco_unitario': preco_unitario,
                'subtotal': subtotal
            })

        # Agora ambos valor_recebido e total_venda são Decimais, a operação é válida
        troco = valor_recebido - total_venda

        if troco < 0:
            messages.error(request, "Valor recebido é insuficiente.")
            return redirect('nova_venda')

        if not itens_para_venda:
            messages.error(request, "Adicione pelo menos um item à venda.")
            return redirect('nova_venda')

        # Cria a venda
        venda = Venda.objects.create(
            funcionario=request.user,
            total=total_venda, # Salvar Decimal
            valor_recebido=valor_recebido, # Salvar Decimal
            troco=troco # Salvar Decimal
        )

        # Cria os itens da venda e atualiza o estoque
        for item_data in itens_para_venda:
            ItemVenda.objects.create(
                venda=venda,
                produto=item_data['produto'],
                quantidade=item_data['quantidade'],
                preco_unitario=item_data['preco_unitario'],
                subtotal=item_data['subtotal'],
                codigo_barras=item_data['codigo_barras']
            )
            # Atualiza a quantidade do produto no estoque geral
            item_data['produto'].quantidade_estoque -= item_data['quantidade']
            item_data['produto'].save()

            # Lógica de baixa de estoque em lotes (priorizando os mais antigos/próximos do vencimento)
            qtd_para_baixar = item_data['quantidade']
            lotes_disponiveis = Lote.objects.filter(
                produto=item_data['produto'],
                quantidade__gt=0
            ).order_by('data_validade', 'data_entrada')

            for lote in lotes_disponiveis:
                if qtd_para_baixar <= 0:
                    break

                qtd_baixar_no_lote = min(qtd_para_baixar, lote.quantidade)
                lote.quantidade -= qtd_baixar_no_lote
                lote.save()
                qtd_para_baixar -= qtd_baixar_no_lote

        messages.success(request, "Venda registrada com sucesso.")
        return redirect('historico_vendas')

    # GET request: exibe a página de nova venda com os produtos disponíveis para o JS
    produtos = Produto.objects.filter(ativo=True).annotate(
        categoria_display=F('categoria')
    ).values('id', 'nome', 'preco', 'codigo_barras', 'categoria', 'quantidade_estoque')
    
    for p in produtos:
        p['categoria_display'] = dict(Produto.CATEGORIAS).get(p['categoria'], p['categoria'])

    return render(request, 'vendas/nova_venda.html', {'produtos_data': list(produtos)})

@login_required
def historico_vendas(request):
    vendas = Venda.objects.select_related('funcionario').prefetch_related('itens__produto').order_by('-data')
    return render(request, 'vendas/historico.html', {'vendas': vendas})