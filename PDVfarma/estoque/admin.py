from django.contrib import admin
from .models import Produto

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'preco', 'quantidade_estoque', 'ativo') 
    list_filter = ('ativo', 'categoria') 
    search_fields = ('nome', 'codigo_barras')