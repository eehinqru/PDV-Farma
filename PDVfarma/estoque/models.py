from django.db import models
from django.db.models import Sum
from django.utils import timezone


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
    quantidade_estoque = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.nome

    def recalcular_quantidade_estoque(self):
        hoje = timezone.now().date()
        # Soma a quantidade de lotes válidos (data_validade maior ou igual a hoje)
        total = self.lotes.filter(data_validade__gte=hoje).aggregate(Sum('quantidade'))['quantidade__sum']
        self.quantidade_estoque = total if total is not None else 0
        self.save()

class Lote(models.Model):
    produto = models.ForeignKey(Produto, related_name='lotes', on_delete=models.CASCADE)
    data_entrada = models.DateField()
    data_validade = models.DateField()
    quantidade = models.IntegerField()

    def __str__(self):
        return f"Lote {self.id} de {self.produto.nome} (Qtd: {self.quantidade}, Val: {self.data_validade})"

    @property
    def esta_vencido(self):
        return self.data_validade < timezone.now().date()