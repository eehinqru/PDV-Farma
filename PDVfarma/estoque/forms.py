from django import forms
from .models import Produto

class ProdutoForm(forms.ModelForm):
    data_validade = forms.DateField(
        input_formats=['%d/%m/%Y', '%Y-%m-%d'],  # aceita ambos os formatos
        widget=forms.DateInput(format='%d/%m/%Y')
    )

    class Meta:
        model = Produto
        fields = '__all__'
        widgets = {
            'categoria': forms.Select(choices=Produto.CATEGORIAS),
        }