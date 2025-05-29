from django import forms
from .models import Produto, Lote
from django.forms import inlineformset_factory

class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = [
            'nome',
            'descricao',
            'preco',
            'categoria',
            'codigo_barras',
            'imagem',
        ]
        widgets = {
            'categoria': forms.Select(choices=Produto.CATEGORIAS),
        }

class LoteForm(forms.ModelForm):
    data_validade = forms.DateField(
        input_formats=['%d/%m/%Y', '%Y-%m-%d'], 
        widget=forms.DateInput(format='%d/%m/%Y', attrs={'placeholder': 'dd/mm/aaaa'})
    )
    data_entrada = forms.DateField(
        input_formats=['%d/%m/%Y', '%Y-%m-%d'],
        widget=forms.DateInput(format='%d/%m/%Y', attrs={'placeholder': 'dd/mm/aaaa'})
    )
    class Meta:
        model = Lote
        fields = ['data_entrada',
                  'data_validade', 
                  'quantidade'
                ]

LoteFormSet = inlineformset_factory(
    Produto,
    Lote,
    form=LoteForm,
    fields=['data_entrada', 'data_validade', 'quantidade'],
    extra=1,
    can_delete=True
)