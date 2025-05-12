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
    
    nome = models.CharField(max_length=200)
    descricao = models.TextField()
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    quantidade_em_estoque = models.IntegerField()
    categoria = models.CharField(max_length=50, choices=CATEGORIAS)
    
    def __str__(self):
        return self.nome
