from django.db import models
from django.contrib.auth.models import User
from estoque.models import Produto

class Venda(models.Model):

    data = models.DateTimeField(auto_now_add=True)
    funcionario = models.ForeignKey(User, on_delete=models.PROTECT)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    valor_recebido = models.DecimalField(max_digits=10, decimal_places=2)
    troco = models.DecimalField(max_digits=10, decimal_places=2)
    
    def _str_(self):
        return f"Venda #{self.id} - {self.data.strftime('%d/%m/%Y %H:%M')}"

class ItemVenda(models.Model):

    venda = models.ForeignKey(Venda, related_name='itens', on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT)
    quantidade = models.PositiveIntegerField()
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    codigo_barras = models.CharField(max_length=20, null=True, blank=True)

    def _str_(self):
        return f"{self.quantidade}x {self.produto.nome} - R$ {self.subtotal}"