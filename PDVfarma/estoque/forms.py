from django import forms
from .models import Produto

class ProdutoForm(forms.ModelForm):
    data_validade = forms.DateField(
        input_formats=['%d/%m/%Y', '%Y-%m-%d'],  # aceita formatos 31/12/2025 e 2025-12-31
        widget=forms.DateInput(format='%d/%m/%Y', attrs={'placeholder': 'dd/mm/aaaa'})
    )
    data_entrada = forms.DateField(
        input_formats=['%d/%m/%Y', '%Y-%m-%d'],
        widget=forms.DateInput(format='%d/%m/%Y', attrs={'placeholder': 'dd/mm/aaaa'})
    )

    class Meta:
        model = Produto
        fields = [
            'nome',
            'descricao',
            'preco',
            'quantidade_em_estoque',
            'categoria',
            'imagem',
            'data_entrada',
            'data_validade',
        ]
        widgets = {
            'categoria': forms.Select(choices=Produto.CATEGORIAS),
        }
