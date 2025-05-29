from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404, redirect
from .models import Produto, Lote
from .forms import ProdutoForm, LoteFormSet
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import timedelta
from django.db.models import Max, Sum
from django.db.models.functions import Coalesce


# View para redirecionar para a listagem de produtos
def estoque(request):
    return redirect('listar_produtos')

# Função para verificar se o usuário é o dono
def eh_dono(user):
    return user.groups.filter(name='dono').exists()

# Função para verificar se o usuário é o funcionário
def is_funcionario(user):
    return user.groups.filter(name='funcionario').exists()

# Função auxiliar para a listagem de produtos
def listar_produtos_query(request):
    query = request.GET.get('q', '')  
    categoria = request.GET.get('categoria', '').strip()  
    categorias = Produto.CATEGORIAS

    produtos = Produto.objects.all()

    if query:
        produtos = produtos.filter(nome__icontains=query)

    if categoria:
        produtos = produtos.filter(categoria=categoria)

    paginator = Paginator(produtos, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return {
        'page_obj': page_obj,
        'query': query,
        'categoria': categoria,
        'categorias': categorias,
    }

@login_required
def listar_produtos(request):
    
    # Verifica se o usuário é dono ou funcionário
    if eh_dono(request.user) or is_funcionario(request.user):
        context = listar_produtos_query(request)
        context['is_dono'] = eh_dono(request.user)
        context['hoje'] = timezone.now().date()
        
        # Adiciona os contadores no contexto
        limite_validade = timezone.now().date() + timedelta(days=30)
        context['perto_validade_count'] = Lote.objects.filter(
            data_validade__lte=limite_validade,
            data_validade__gte=timezone.now().date()
        ).count()
        
        context['vencidos_count'] = Lote.objects.filter(
            data_validade__lt=timezone.now().date()
        ).count()
        
        Produto.objects.annotate(
            quantidade_total=Coalesce(Sum('lotes__quantidade'), 0)
        ).filter(
            quantidade_total__lte=5
        ).count()

        

        return render(request, 'estoque/lista_produtos.html', context)
    
    return redirect('login')


@login_required
@user_passes_test(eh_dono)
def criar_produto(request):
    if request.method == 'POST':
        form = ProdutoForm(request.POST, request.FILES)
        produto_temp = Produto()  # usado para inicializar o formset antes de salvar o produto real

        if form.is_valid():
            produto = form.save(commit=False)
            formset = LoteFormSet(request.POST, instance=produto)

            if formset.is_valid():
                produto.save()
                formset.instance = produto
                formset.save()
                return redirect('listar_produtos')
        else:
            formset = LoteFormSet(request.POST, instance=produto_temp)

    else:
        form = ProdutoForm()
        formset = LoteFormSet(instance=Produto())

    return render(request, 'estoque/form.html', {
        'form': form,
        'formset': formset,
        'is_edit': False,
    })


# Atualizar um produto - Somente o dono pode atualizar
@login_required
@user_passes_test(eh_dono)
def atualizar_produto(request, id):
    produto = get_object_or_404(Produto, id=id)

    if request.method == 'POST':
        form = ProdutoForm(request.POST, request.FILES, instance=produto)
        formset = LoteFormSet(request.POST, instance=produto)

        if form.is_valid() and formset.is_valid():
            produto = form.save(commit=False)
            produto.save()

            formset.instance = produto
            lotes = formset.save(commit=False)

            # Pega o último número salvo dos lotes existentes
            ultimo_numero = produto.lotes.aggregate(max_num=Max('numero'))['max_num'] or 0

            for idx, lote in enumerate(lotes, start=1):
                if not lote.numero:  # só para os novos lotes
                    lote.numero = ultimo_numero + idx
                lote.produto = produto
                lote.save()

            # Apaga lotes marcados para exclusão
            for lote in formset.deleted_objects:
                lote.delete()

            return redirect('listar_produtos')

    else:
        form = ProdutoForm(instance=produto)
        formset = LoteFormSet(instance=produto)

    return render(request, 'estoque/form.html', {
        'form': form,
        'formset': formset,
        'is_edit': True,
        'produto': produto,
    })


# Deletar um produto - Somente o dono pode deletar
@login_required
@user_passes_test(eh_dono)
def deletar_produto(request, id):
    produto = get_object_or_404(Produto, id=id)
    if request.method == 'POST':
        produto.delete()
        return redirect('listar_produtos') 
    return render(request, 'estoque/confirmar_delete.html', {'produto': produto})


# Dashboard - Exibe contadores de produtos perto da validade e com baixa quantidade        
@login_required
def dashboard(request):
    hoje = timezone.localdate()
    limite_validade = hoje + timedelta(days=30)
    
    perto_validade_count = Lote.objects.filter(
        data_validade__lte=limite_validade,
        data_validade__gte=hoje
    ).count()
    
    vencidos_count = Lote.objects.filter(
        data_validade__lt=hoje
    ).count()

    baixa_quantidade_count = Produto.objects.annotate(
        quantidade_total=Sum('lotes__quantidade')
    ).filter(
        quantidade_total__lte=5
    ).count()

    context = {
        'vencidos_count': vencidos_count, 
        'perto_validade_count': perto_validade_count,
        'baixa_quantidade_count': baixa_quantidade_count,
        'hoje': hoje,
        'limite_validade': limite_validade,
    }

    return render(request, 'estoque/dashboard.html', context)


