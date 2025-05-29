# models.py
from django.db.models import Sum
from django.db import models

class Produto(models.Model):
    CATEGORIAS = [
        ('medicamento', 'Medicamento'),
        ('cosmetico', 'Cosmético'),
        ('suplemento', 'Suplemento'),
        ('higiene', 'Higiene Pessoal'),
        ('perfumaria', 'Perfumaria'),
        ('bem_estar', 'Bem-estar'),
        ('veterinario', 'Produtos Veterinários'),
    ]

    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.CharField(max_length=100, choices=CATEGORIAS)
    codigo_barras = models.CharField(max_length=100, unique=True)
    imagem = models.ImageField(upload_to='produtos/', blank=True, null=True)

    def __str__(self):
        return self.nome
class Lote(models.Model):
    produto = models.ForeignKey(Produto, related_name='lotes', on_delete=models.CASCADE)
    data_entrada = models.DateField()
    data_validade = models.DateField()
    quantidade = models.IntegerField()

    def __str__(self):
        return f"Lote de {self.produto.nome} ({self.data_validade})"
@property
def quantidade_total(self):
    total = self.lotes.aggregate(soma=Sum('quantidade'))['soma']
    return total or 0
