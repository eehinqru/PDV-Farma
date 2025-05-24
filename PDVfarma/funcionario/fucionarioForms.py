from django import forms
from .models import Funcionario
from django.forms.widgets import DateInput

class FuncionarioForm(forms.ModelForm):
    data_nascimento = forms.DateField(
        input_formats=['%d/%m/%Y'],
        widget=DateInput(format='%d/%m/%Y', attrs={'placeholder': 'dd/mm/aaaa'}),
        label="Data de Nascimento"
    )
    
    class Meta:
        model = Funcionario
        fields = ['telefone', 'cpf', 'endereco', 'sexo', 'data_nascimento', 'foto', 'observacao']