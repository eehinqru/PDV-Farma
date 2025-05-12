from django import forms
from .models import Produto

class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ['nome', 'descricao', 'preco', 'quantidade_em_estoque', 'categoria']
        widgets = {
            'categoria': forms.Select(choices=Produto.CATEGORIAS),
        }