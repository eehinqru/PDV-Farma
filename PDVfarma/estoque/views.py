from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404, redirect
from .models import Produto
from .forms import ProdutoForm
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import timedelta


def estoque(request):
    return redirect('listar_produtos')

# Função para verificar se o usuário é o dono
def is_dono(user):
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
    if is_dono(request.user) or is_funcionario(request.user):
        context = listar_produtos_query(request)
        context['hoje'] = timezone.now().date()
          # Adiciona os contadores no contexto
        limite_validade = timezone.now().date() + timedelta(days=30)
        context['perto_validade_count'] = Produto.objects.filter(
            data_validade__lte=limite_validade,
            data_validade__gte=timezone.now().date()
        ).count()
        context['baixa_quantidade_count'] = Produto.objects.filter(
            quantidade_em_estoque__lte=5
        ).count()

        return render(request, 'estoque/lista_produtos.html', context)
    # Caso contrário, redireciona para a página de login
    return redirect('login')


# Criar novo produto - Somente o dono pode criar
@login_required
@user_passes_test(is_dono)
def criar_produto(request):
    if request.method == 'POST':
        form = ProdutoForm(request.POST, request.FILES)  
        if form.is_valid():
            form.save()
            return redirect('listar_produtos')  # Redireciona para a lista de produtos
    else:
        form = ProdutoForm()
    return render(request, 'estoque/form.html', {'form': form})

# Atualizar um produto - Somente o dono pode atualizar
@login_required
@user_passes_test(is_dono)
def atualizar_produto(request, id):
    produto = get_object_or_404(Produto, id=id)
    if request.method == 'POST':
        form = ProdutoForm(request.POST, instance=produto)
        if form.is_valid():
            form.save()
            return redirect('listar_produtos')  # Redireciona para a lista de produtos
    else:
        form = ProdutoForm(instance=produto)
    return render(request, 'estoque/form.html', {'form': form})

# Deletar um produto - Somente o dono pode deletar
@login_required
@user_passes_test(is_dono)
def deletar_produto(request, id):
    produto = get_object_or_404(Produto, id=id)
    if request.method == 'POST':
        produto.delete()
        return redirect('listar_produtos')  # Redireciona para a lista de produtos
    return render(request, 'estoque/confirmar_delete.html', {'produto': produto})

        
@login_required
def dashboard(request):
    limite_validade = timezone.now().date() + timedelta(days=30)
    perto_validade_count = Produto.objects.filter(
        data_validade__lte=limite_validade,
        data_validade__gte=timezone.now().date()
    ).count()

    baixa_quantidade_count = Produto.objects.filter(quantidade_em_estoque = 5).count()

    context = {
        'perto_validade_count': perto_validade_count,
        'baixa_quantidade_count': baixa_quantidade_count,
    }

    return render(request, 'estoque/dashboard.html', context)

# produtos_vencidos = Produto.objects.filter(
#    data_validade__lt=timezone.now().date()
#)

