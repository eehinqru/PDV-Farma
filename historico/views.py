from django.shortcuts import render

# Create your views here.

def historico(request):
    return render(request, 'historico.html')