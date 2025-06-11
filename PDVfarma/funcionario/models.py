from django.contrib.auth.models import User
from django.db import models

class Funcionario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)  # ALTERADO TEMPORARIAMENTE

    SEXO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Feminino'),
        ('O', 'Outros'),
    ]

    telefone = models.CharField(max_length=15)
    cpf = models.CharField(max_length=14, unique=True)
    endereco = models.CharField(max_length=255)
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)
    data_nascimento = models.DateField()

    foto = models.ImageField(upload_to='fotos_funcionarios/', blank=True, null=True)
    observacao = models.TextField(blank=True, null=True)

    criado_em = models.DateTimeField(auto_now_add=True)
 
