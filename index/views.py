from django.shortcuts import render #, redirect 

# direcionar a raiz do aplicativo para a página inicial
def index(request):

    return render(request, 'index/index.html')

