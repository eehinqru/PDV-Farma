from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # Redirecionamento com base no grupo do usuário
            if user.groups.filter(name='dono').exists():
                return redirect('estoque')  # redireciona pra tela de estoque
            elif user.groups.filter(name='funcionario').exists():
                return redirect('vendas')   # redireciona pra tela de vendas

            return redirect('home')

        else:
            messages.error(request, "Email ou senha inválidos.")

    return render(request, 'login/login.html')
