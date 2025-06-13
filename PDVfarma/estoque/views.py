from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404, redirect
from .models import Produto, Lote
from vendas.models import Venda, ItemVenda
from .forms import ProdutoForm, LoteFormSet
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q, Sum, F, ExpressionWrapper, DecimalField, Count 
from django.db.models.functions import Coalesce
from django.db import transaction
from django.contrib import messages
from funcionario.models import Funcionario
from decimal import Decimal

# Redireciona para a listagem de produtos.
def estoque(request):
    return redirect('listar_produtos')

# Verifica se o usuário pertence ao grupo 'dono'.
def eh_dono(user):
    return user.groups.filter(name='dono').exists()

# Verifica se o usuário pertence ao grupo 'funcionario'.
def is_funcionario(user):
    return user.groups.filter(name='funcionario').exists()

# Lista produtos com filtros de pesquisa, categoria e validade.
@login_required
def listar_produtos(request):
    if not (eh_dono(request.user) or is_funcionario(request.user)):
        return redirect('login')

    query = request.GET.get('q', '')
    categoria_valor = request.GET.get('categoria', '')
    validade_proxima_filter_ativado = request.GET.get('validade_proxima', '') == 'true'
    
    status_validade_filter = request.GET.get('status_validade', '')
    baixo_estoque_filter_ativado = request.GET.get('baixo_estoque', '') == 'true'

    hoje = timezone.now().date()
    dias_validade_proxima = 90
    limite_data_validade_proxima = hoje + timedelta(days=dias_validade_proxima)

    produtos_qs = Produto.objects.filter(ativo=True).order_by('nome')

    if query:
        produtos_qs = produtos_qs.filter(
            Q(nome__icontains=query) | Q(codigo_barras__icontains=query)
        )

    if categoria_valor:
        produtos_qs = produtos_qs.filter(categoria=categoria_valor)
    

    if validade_proxima_filter_ativado:
        produtos_com_lotes_proximos_vencimento = Produto.objects.filter(
            lotes__data_validade__gte=hoje,
            lotes__data_validade__lte=limite_data_validade_proxima
        ).distinct()
        produtos_qs = produtos_qs.filter(id__in=produtos_com_lotes_proximos_vencimento.values('id'))
    
    if status_validade_filter == 'vencido':
        produtos_vencidos = Produto.objects.filter(
            lotes__data_validade__lt=hoje
        ).distinct()
        produtos_qs = produtos_qs.filter(id__in=produtos_vencidos.values('id'))
    
    if baixo_estoque_filter_ativado:
        produtos_qs = produtos_qs.filter(quantidade_estoque__lte=5)


    produtos_para_exibir_com_status = []
    for produto in produtos_qs.distinct(): 
        produto_data = {
            'id': produto.id,
            'nome': produto.nome,
            'descricao': produto.descricao,
            'preco': produto.preco,
            'categoria': produto.categoria,
            'get_categoria_display': produto.get_categoria_display(),
            'codigo_barras': produto.codigo_barras,
            'imagem': produto.imagem,
            'quantidade_estoque': produto.quantidade_estoque,
            'status_validade': 'ok',
            'data_validade_mais_proxima': None, 
        }

        lotes_do_produto_atual = produto.lotes.all()
        
        lote_mais_proximo_vencimento = None
        lote_vencido_mais_antigo = None

        for lote in lotes_do_produto_atual:
            if lote.data_validade < hoje:
                if lote_vencido_mais_antigo is None or lote.data_validade < lote_vencido_mais_antigo.data_validade:
                    lote_vencido_mais_antigo = lote
            elif lote.data_validade > hoje and lote.data_validade <= limite_data_validade_proxima: 
                if lote_mais_proximo_vencimento is None or lote.data_validade < lote_mais_proximo_vencimento.data_validade:
                    lote_mais_proximo_vencimento = lote

        if lote_vencido_mais_antigo:
            produto_data['status_validade'] = 'vencido'
            produto_data['data_validade_mais_proxima'] = lote_vencido_mais_antigo.data_validade
        elif lote_mais_proximo_vencimento:
            produto_data['status_validade'] = 'perto_vencer'
            produto_data['data_validade_mais_proxima'] = lote_mais_proximo_vencimento.data_validade
        
        produtos_para_exibir_com_status.append(produto_data)

    paginator = Paginator(produtos_para_exibir_com_status, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    lotes_filtrados_geral = Lote.objects.filter(produto__in=produtos_qs) 

    perto_validade_count_geral = lotes_filtrados_geral.filter(
        data_validade__gt=hoje,
        data_validade__lte=limite_data_validade_proxima
    ).count()

    vencidos_count_geral = lotes_filtrados_geral.filter(
        data_validade__lt=hoje
    ).count()

    baixa_quantidade_count_geral = produtos_qs.filter( 
        quantidade_estoque__lte=5
    ).count()

    total_produtos_filtrados = produtos_qs.count() 
    total_lotes_filtrados = lotes_filtrados_geral.count()
    quantidade_total_itens_filtrados = lotes_filtrados_geral.aggregate(Sum('quantidade'))['quantidade__sum'] or 0
    valor_total_estoque_filtrado = lotes_filtrados_geral.annotate(
        valor_lote=ExpressionWrapper(F('quantidade') * F('produto__preco'), output_field=DecimalField())
    ).aggregate(Sum('valor_lote'))['valor_lote__sum'] or 0.00
    
    count_produtos_com_validade_proxima = Produto.objects.filter(
        lotes__data_validade__gte=hoje,
        lotes__data_validade__lte=limite_data_validade_proxima
    ).filter(pk__in=produtos_qs.values('pk')).distinct().count()

    context = {
        'page_obj': page_obj,
        'query_param': query,
        'categoria_param': categoria_valor,
        'todas_categorias': Produto.CATEGORIAS,
        'validade_proxima_param_ativado': validade_proxima_filter_ativado,
        'status_validade_param': status_validade_filter,
        'baixo_estoque_param_ativado': baixo_estoque_filter_ativado,

        'total_produtos_exibidos': total_produtos_filtrados,
        'total_lotes_exibidos': total_lotes_filtrados,
        'quantidade_total_itens_exibidos': quantidade_total_itens_filtrados,
        'valor_total_estoque_exibido': valor_total_estoque_filtrado,
        'produtos_com_validade_proxima_exibidos': count_produtos_com_validade_proxima, 
        'dias_para_validade_proxima': dias_validade_proxima, 

        'perto_validade_count_geral': perto_validade_count_geral,
        'vencidos_count_geral': vencidos_count_geral,
        'baixa_quantidade_count_geral': baixa_quantidade_count_geral,

        'hoje': hoje, 
        'is_dono': eh_dono(request.user), 
    }
    return render(request, 'estoque/listar_produtos.html', context)

# Cria um novo produto e seus lotes.
@login_required
@user_passes_test(eh_dono)
def criar_produto(request):
    if request.method == 'POST':
        form = ProdutoForm(request.POST, request.FILES)
        
        if form.is_valid():
            produto = form.save() 
            formset = LoteFormSet(request.POST, instance=produto) 
            if formset.is_valid():
                formset.save() 
                produto.recalcular_quantidade_estoque()
                return redirect('listar_produtos')
            else:
                return render(request, 'estoque/form.html', {
                    'form': form,
                    'formset': formset,
                    'produto': produto, 
                    'is_edit': False,
                })
        else:
            formset = LoteFormSet(request.POST, instance=Produto()) 
            return render(request, 'estoque/form.html', {
                'form': form,
                'formset': formset,
                'is_edit': False,
            })
    else:
        form = ProdutoForm()
        formset = LoteFormSet(instance=Produto())

    return render(request, 'estoque/form.html', {
        'form': form,
        'formset': formset,
        'is_edit': False,
    })

# Atualiza um produto existente e seus lotes.
@login_required
@user_passes_test(eh_dono)
def atualizar_produto(request, id):
    produto = get_object_or_404(Produto, id=id)

    if request.method == 'POST':
        form = ProdutoForm(request.POST, request.FILES, instance=produto)
        formset = LoteFormSet(request.POST, instance=produto)

        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            produto.recalcular_quantidade_estoque()
            return redirect('listar_produtos')
        else:
            print("Erros no formulário de produto:", form.errors)
            print("Erros no formset de lotes:", formset.errors)
            return render(request, 'estoque/form.html', {
                'form': form,
                'formset': formset,
                'is_edit': True,
                'produto': produto,
            })
    else:
        form = ProdutoForm(instance=produto)
        formset = LoteFormSet(instance=produto)

    return render(request, 'estoque/form.html', {
        'form': form,
        'formset': formset,
        'is_edit': True,
        'produto': produto,
    })

# Deleta um produto.
@login_required
@user_passes_test(eh_dono)
def deletar_produto(request, produto_id):
    if not eh_dono(request.user):
        print(f"DEBUG: ERRO ao desativar produto {produto_id}: {e}")  # noqa: F821
        messages.error(request, "Você não tem permissão para desativar produtos.")
        return redirect('listar_produtos')
    
    produto = get_object_or_404(Produto, id=produto_id)

    if request.method == 'POST':
        try:
            produto.ativo = False 
            produto.save()
            messages.success(request, f'Produto "{produto.nome}" desativado com sucesso.')
            return redirect('listar_produtos')
        except Exception as e:
            print(f"DEBUG: ERRO ao desativar produto {produto_id}: {e}")
            messages.error(request, f"Ocorreu um erro ao desativar o produto: {e}")
            return redirect('listar_produtos')
    
    messages.error(request, "Requisição inválida. Use o método POST para desativar produtos.")
    return redirect('listar_produtos') 

# Exibe o dashboard com indicadores gerais do estoque.
@login_required
def dashboard(request):
    hoje = timezone.localdate()
    limite_validade_dashboard = hoje + timedelta(days=90) 
    
    # Indicadores principais do estoque
    # 1. Contagem de Lotes Vencidos
    vencidos_count = Lote.objects.filter(
        produto__ativo=True,
        data_validade__lt=hoje
    ).count()

    # 2. Contagem de Lotes Perto da Validade (dentro dos próximos 90 dias)
    perto_validade_count = Lote.objects.filter(
        produto__ativo=True,
        data_validade__gte=hoje,
        data_validade__lte=limite_validade_dashboard,
        
    ).count()

    # 3. Contagem de Produtos com Baixo Estoque (<= 5 unidades)
    baixa_quantidade_count = Produto.objects.filter(
        quantidade_estoque__lte=5,
        ativo=True
    ).count()

    # 4. Total de Produtos Ativos
    total_produtos_ativos = Produto.objects.filter(ativo=True).count()

    # 5. Quantidade Total de Itens em Estoque (considera apenas lotes não vencidos de produtos ativos)
    quantidade_total_itens = Lote.objects.filter(
        data_validade__gte=hoje
    ).aggregate(total=Coalesce(Sum('quantidade'), 0))['total']

    # 6. Valor Total do Estoque (considera apenas produtos ativos e lotes não vencidos)
    valor_total_estoque = Lote.objects.filter(
        data_validade__gte=hoje
    ).annotate(
        valor_lote=ExpressionWrapper(F('quantidade') * F('produto__preco'), output_field=DecimalField())
    ).aggregate(total=Coalesce(Sum('valor_lote'), Decimal('0.00')))['total']

    # 7. Produtos por Categoria (para um gráfico ou tabela)
    produtos_por_categoria = Produto.objects.filter(ativo=True).values('categoria').annotate(
        count=Count('id')
    ).order_by('categoria')

    categorias_display = {k: v for k, v in Produto.CATEGORIAS}
    produtos_por_categoria_display = [
        {'nome': categorias_display.get(item['categoria'], item['categoria']), 'count': item['count']}
        for item in produtos_por_categoria
    ]
    
    # 8. Número de vendas no mês
    vendas_no_mes = Venda.objects.filter(
        data__year=hoje.year,
        data__month=hoje.month
    )
    numero_vendas_mes = vendas_no_mes.count()

    # 9. Dinheiro feito no mês (faturamento total)
    dinheiro_feito_mes = vendas_no_mes.aggregate(total_faturado=Coalesce(Sum('total'), Decimal('0.00')))['total_faturado']

    # 10. Funcionário que fez mais vendas no mês
    funcionario_mais_vendas_mes = None
    vendas_por_funcionario = vendas_no_mes.values('funcionario__first_name', 'funcionario__last_name').annotate(
        num_vendas=Count('id')
    ).order_by('-num_vendas') 

    if vendas_por_funcionario:
        top_vendedor = vendas_por_funcionario.first() 
        nome_completo = top_vendedor['funcionario__first_name']
        if top_vendedor['funcionario__last_name']:
            nome_completo += f" {top_vendedor['funcionario__last_name']}"
        funcionario_mais_vendas_mes = {
            'nome': nome_completo,
            'num_vendas': top_vendedor['num_vendas']
        }

    funcionario_logado = None
    if request.user.is_authenticated:
        try:
            funcionario_logado = request.user.funcionario
        except Funcionario.DoesNotExist:
            pass

    is_dono_context = eh_dono(request.user)

    context = {
        # Métricas de Estoque
        'vencidos_count': vencidos_count, 
        'perto_validade_count': perto_validade_count,
        'baixa_quantidade_count': baixa_quantidade_count,
        'total_produtos_ativos': total_produtos_ativos,
        'quantidade_total_itens': quantidade_total_itens,
        'valor_total_estoque': valor_total_estoque,
        'produtos_por_categoria': produtos_por_categoria_display,
        
        # Métricas de Vendas
        'numero_vendas_mes': numero_vendas_mes,
        'dinheiro_feito_mes': dinheiro_feito_mes,
        'funcionario_mais_vendas_mes': funcionario_mais_vendas_mes,

        # Informações gerais do dashboard e usuário
        'hoje': hoje,
        'limite_validade_dashboard': limite_validade_dashboard,
        'is_dono': is_dono_context,
        'funcionario_logado': funcionario_logado,
    }

    return render(request, 'estoque/dashboard.html', context)

# Nova lógica para a tela de vendas
@login_required
@transaction.atomic
def nova_venda(request):
    if request.method == 'POST':
        total_itens = int(request.POST.get('total_itens', 0))
        valor_recebido = float(request.POST.get('valor_recebido', 0))

        itens_para_venda = []
        total_venda = 0

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
            
            preco_unitario = produto.preco
            subtotal = preco_unitario * quantidade
            total_venda += subtotal

            itens_para_venda.append({
                'produto': produto,
                'quantidade': quantidade,
                'preco_unitario': preco_unitario,
                'subtotal': subtotal
            })

        troco = valor_recebido - total_venda

        if troco < 0:
            messages.error(request, "Valor recebido é insuficiente.")
            return redirect('nova_venda')

        if not itens_para_venda:
            messages.error(request, "Adicione pelo menos um item à venda.")
            return redirect('nova_venda')

        venda = Venda.objects.create(
            funcionario=request.user,
            total=total_venda,
            valor_recebido=valor_recebido,
            troco=troco
        )

        # Cria os itens da venda e atualiza o estoque
        for item_data in itens_para_venda:
            ItemVenda.objects.create(
                venda=venda,
                produto=item_data['produto'],
                quantidade=item_data['quantidade'],
                preco_unitario=item_data['preco_unitario'],
                subtotal=item_data['subtotal']
            )
            # Atualiza a quantidade do produto no estoque
            item_data['produto'].quantidade_estoque -= item_data['quantidade']
            item_data['produto'].save()


            lotes_disponiveis = Lote.objects.filter(
                produto=item_data['produto'],
                quantidade__gt=0
            ).order_by('data_validade', 'data_entrada')

            qtd_para_baixar = item_data['quantidade']
            for lote in lotes_disponiveis:
                if qtd_para_baixar <= 0:
                    break
                
                qtd_baixar_no_lote = min(qtd_para_baixar, lote.quantidade)
                lote.quantidade -= qtd_baixar_no_lote
                lote.save()
                qtd_para_baixar -= qtd_baixar_no_lote


        messages.success(request, "Venda registrada com sucesso.")
        return redirect('historico_vendas')

# exibe a página de nova venda com os produtos disponíveis  
    produtos = Produto.objects.all().annotate(

        categoria_display=F('categoria') 
    ).values('id', 'nome', 'preco', 'codigo_barras', 'categoria', 'quantidade_estoque')
    

    for p in produtos:
        p['categoria_display'] = dict(Produto.CATEGORIAS).get(p['categoria'], p['categoria'])

    return render(request, 'vendas/nova_venda.html', {'produtos_data': list(produtos)})

# Histórico de vendas
@login_required
def historico_vendas(request):
    vendas = Venda.objects.select_related('funcionario').prefetch_related('itens__produto').order_by('-data')
    return render(request, 'vendas/historico.html', {'vendas': vendas})