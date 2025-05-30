from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404, redirect
from .models import Produto, Lote
from .forms import ProdutoForm, LoteFormSet
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q, Sum, F, ExpressionWrapper, DecimalField

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

    hoje = timezone.now().date()
    dias_validade_proxima = 90
    limite_data_validade_proxima = hoje + timedelta(days=dias_validade_proxima)

    produtos_qs = Produto.objects.all().order_by('nome')

    if query:
        produtos_qs = produtos_qs.filter(
            Q(nome__icontains=query) | Q(codigo_barras__icontains=query)
        )

    if categoria_valor:
        produtos_qs = produtos_qs.filter(categoria=categoria_valor)
    
    # Esta consulta encontra lotes próximos do vencimento APENAS para os produtos já filtrados
    lotes_proximos_vencimento_qset = Lote.objects.filter(
        produto__in=produtos_qs,  # Garante que os lotes são dos produtos filtrados até agora
        data_validade__gte=hoje,
        data_validade__lte=limite_data_validade_proxima
    )
    
    # Produtos que possuem QUALQUER lote com validade próxima (para o indicador e filtro)
    produtos_com_lotes_proximos_vencimento = Produto.objects.filter(
        pk__in=lotes_proximos_vencimento_qset.values('produto__pk')
    ).distinct()

    if validade_proxima_filter_ativado:
        # Se o filtro "somente validade próxima" estiver ativado, restrinja produtos_qs
        produtos_qs = produtos_qs.filter(id__in=produtos_com_lotes_proximos_vencimento.values('id'))

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
    
    # --- CÁLCULOS DOS INDICADORES AGORA BASEADOS NO 'produtos_qs' FILTRADO ---
    # Contagem de lotes próximos da validade para os produtos EXIBIDOS na tela
    perto_validade_count_geral = Lote.objects.filter(
        produto__in=produtos_qs, # Filtra por produtos na tela
        data_validade__gt=hoje,
        data_validade__lte=limite_data_validade_proxima
    ).count()

    # Contagem de lotes vencidos para os produtos EXIBIDOS na tela
    vencidos_count_geral = Lote.objects.filter(
        produto__in=produtos_qs, # Filtra por produtos na tela
        data_validade__lt=hoje
    ).count()

    # Contagem de produtos com baixa quantidade de estoque para os produtos EXIBIDOS na tela
    baixa_quantidade_count_geral = produtos_qs.filter( # Usa diretamente o produtos_qs filtrado
        quantidade_estoque__lte=5
    ).count()

    # (Os indicadores 'total_produtos_exibidos', 'total_lotes_exibidos', etc., já estavam corretos
    # pois usavam 'produtos_qs' ou subconsultas baseadas nele.)
    total_produtos_filtrados = produtos_qs.count() 

    lotes_filtrados_total = Lote.objects.filter(produto__in=produtos_qs)
    total_lotes_filtrados = lotes_filtrados_total.count()

    quantidade_total_itens_filtrados = lotes_filtrados_total.aggregate(Sum('quantidade'))['quantidade__sum'] or 0

    valor_total_estoque_filtrado = lotes_filtrados_total.annotate(
        valor_lote=ExpressionWrapper(F('quantidade') * F('produto__preco'), output_field=DecimalField())
    ).aggregate(Sum('valor_lote'))['valor_lote__sum'] or 0.00

    count_produtos_com_validade_proxima = produtos_com_lotes_proximos_vencimento.count()


    context = {
        'page_obj': page_obj,
        'query_param': query,
        'categoria_param': categoria_valor,
        'todas_categorias': Produto.CATEGORIAS,
        'validade_proxima_param_ativado': validade_proxima_filter_ativado,

        # Indicadores que refletem os filtros aplicados (PARA A TELA ATUAL DE PRODUTOS)
        # ESTES SÃO OS INDICADORES QUE AGORA SERÃO COERENTES COM O FILTRO
        'perto_validade_count_geral': perto_validade_count_geral,
        'vencidos_count_geral': vencidos_count_geral,
        'baixa_quantidade_count_geral': baixa_quantidade_count_geral,

        # Se você quiser manter esses também, eles já são baseados nos produtos filtrados
        'total_produtos_exibidos': total_produtos_filtrados,
        'total_lotes_exibidos': total_lotes_filtrados,
        'quantidade_total_itens_exibidos': quantidade_total_itens_filtrados,
        'valor_total_estoque_exibido': valor_total_estoque_filtrado,
        'produtos_com_validade_proxima_exibidos': count_produtos_com_validade_proxima, 
        'dias_para_validade_proxima': dias_validade_proxima, 

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
                # Chame o recalcular_quantidade_estoque após salvar lotes
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
            # Chame o recalcular_quantidade_estoque após salvar lotes
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
def deletar_produto(request, id):
    produto = get_object_or_404(Produto, id=id)
    if request.method == 'POST':
        produto.delete()
        return redirect('listar_produtos') 
    return render(request, 'estoque/confirmar_delete.html', {'produto': produto})

# Exibe o dashboard com indicadores gerais do estoque.
@login_required
def dashboard(request):
    hoje = timezone.localdate()
    limite_validade_dashboard = hoje + timedelta(days=90) 
    
    perto_validade_count = Lote.objects.filter(
        data_validade__gt=hoje,
        data_validade__lte=limite_validade_dashboard
    ).count()
    
    vencidos_count = Lote.objects.filter(
        data_validade__lt=hoje
    ).count()

    baixa_quantidade_count = Produto.objects.filter(
        quantidade_estoque__lte=5
    ).count()

    context = {
        'vencidos_count': vencidos_count, 
        'perto_validade_count': perto_validade_count,
        'baixa_quantidade_count': baixa_quantidade_count,
        'hoje': hoje,
        'limite_validade': limite_validade_dashboard,
    }

    return render(request, 'estoque/dashboard.html', context)