from django.shortcuts import render

# Create your views here.

def funcionario(request):
    return render(request,'funcionario.html')