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
    imagem = models.ImageField(upload_to='produtos/', blank=True, null=True)
    data_entrada = models.DateField(verbose_name='Data de Entrada', auto_now_add=False, null=True, blank=True)
    data_validade = models.DateField(verbose_name='Data de Validade', null=True, blank=True) 
     
    def __str__(self):
        return self.nome
