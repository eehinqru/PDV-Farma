from .models import Funcionario
from django.contrib.auth.models import Group 

def funcionario_logado_context(request):
    funcionario_logado = None
    if request.user.is_authenticated:
        try:
            funcionario_logado = request.user.funcionario
        except Funcionario.DoesNotExist:
            pass
    return {'funcionario_logado': funcionario_logado}

def is_dono_context(request):
    is_dono_var = False
    if request.user.is_authenticated:
        is_dono_var = request.user.groups.filter(name='dono').exists()
    return {'is_dono': is_dono_var}