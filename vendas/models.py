from django.db import models
from django.contrib.auth.models import User
from estoque.models import Produto

class Venda(models.Model):
    
    FORMA_PAGAMENTO_CHOICES = [
        ('DINHEIRO', 'Dinheiro'),
        ('PIX', 'Pix'),
        ('CARTAO_CREDITO', 'Cartão de Crédito'),
        ('CARTAO_DEBITO', 'Cartão de Débito'),
    ]

    data = models.DateTimeField(auto_now_add=True)
    funcionario = models.ForeignKey(User, on_delete=models.PROTECT)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    valor_recebido = models.DecimalField(max_digits=10, decimal_places=2)
    troco = models.DecimalField(max_digits=10, decimal_places=2)
    forma_pagamento = models.CharField(
        max_length=20, 
        choices=FORMA_PAGAMENTO_CHOICES, 
        default='DINHEIRO' # Valor padrão
    )
    
    def __str__(self):
        return f"Venda #{self.id} - {self.data.strftime('%d/%m/%Y %H:%M')}"

class ItemVenda(models.Model):

    venda = models.ForeignKey(Venda, related_name='itens', on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT)
    quantidade = models.PositiveIntegerField()
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    codigo_barras = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return f"{self.quantidade}x {self.produto.nome} - R$ {self.subtotal}"