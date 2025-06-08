from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
# aplicação de login para autenticar usuários
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        senha = request.POST.get('password')
        user = authenticate(request, username=username, password=senha)

        if user:
            login(request, user)
            return redirect('listar_produtos')  
        else:
            messages.error(request, 'Usuário ou senha inválidos.')

    return render(request, 'login/login.html')

@login_required 
def logout_view(request):
    logout(request) 
    messages.success(request, "Você foi desconectado com sucesso.")
    return redirect('login') 

