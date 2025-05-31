from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.shortcuts import render, redirect
from .models import Funcionario
from .fucionarioForms import FuncionarioForm 
from .userForms import UserForm
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q 

# checar se o usuário é do grupo 'dono'
def is_dono(user):
    return user.groups.filter(name='dono').exists()

@login_required
def listar_funcionarios(request):
    if not is_dono(request.user):
        return redirect('login')

    query = request.GET.get('q', '') 
    

    funcionarios_qs = Funcionario.objects.all().order_by('user__first_name', 'user__last_name') 

    if query:
        funcionarios_qs = funcionarios_qs.filter(
            Q(user__first_name__icontains=query) | 
            Q(user__last_name__icontains=query) | 
            Q(user__email__icontains=query) | 
            Q(telefone__icontains=query)
        ).distinct() 


    paginator = Paginator(funcionarios_qs, 10) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'funcionarios/listar.html', {
        'page_obj': page_obj, 
        'query': query 
    })

# registrar um novo funcionário
@login_required
def registrar_funcionario(request):
    if not is_dono(request.user):
        return redirect('login') 

    if request.method == 'POST':
        user_form = UserForm(request.POST)
        funcionario_form = FuncionarioForm(request.POST, request.FILES)

        if user_form.is_valid() and funcionario_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.save()

            grupo_funcionario = Group.objects.get(name='funcionario')
            user.groups.add(grupo_funcionario)

            funcionario = funcionario_form.save(commit=False)
            funcionario.user = user
            funcionario.save()

            print("Funcionário criado com sucesso!")
            return redirect('listar_funcionarios') 
        else:
            print("Erros no formulário:")
            print(user_form.errors)
            print(funcionario_form.errors)
    else:
        user_form = UserForm()
        funcionario_form = FuncionarioForm()

    return render(request, 'funcionarios/registrar.html', {
        'user_form': user_form,
        'funcionario_form': funcionario_form,
    })

# editar um funcionário existente
@login_required
def editar_funcionario(request, funcionario_id):
    if not is_dono(request.user):
        return redirect('login')

    funcionario = get_object_or_404(Funcionario, id=funcionario_id)
    user = funcionario.user

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        funcionario_form = FuncionarioForm(request.POST, request.FILES, instance=funcionario)

        if user_form.is_valid() and funcionario_form.is_valid():
            user = user_form.save(commit=False)

            senha = user_form.cleaned_data.get('password')
            if senha:
                user.set_password(senha)   

            user.save()
            funcionario_form.save()

            return redirect('listar_funcionarios') 
        else:
            print("Erros nos formulários:")
            print(user_form.errors)
            print(funcionario_form.errors)
    else:
        user_form = UserForm(instance=user)
        funcionario_form = FuncionarioForm(instance=funcionario)

    return render(request, 'funcionarios/registrar.html', {
        'user_form': user_form,
        'funcionario_form': funcionario_form,
        'edicao': True,
        'funcionario': funcionario,
    })

# deletar um funcionário        
@login_required
def deletar_funcionario(request, funcionario_id):
    if not is_dono(request.user):
        return redirect('login')

    funcionario = get_object_or_404(Funcionario, id=funcionario_id)
    
    funcionario.delete()
    return redirect('listar_funcionarios') 

