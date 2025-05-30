from django import forms
from django.forms import modelformset_factory, BaseModelFormSet
from .models import ItemVenda, Produto

class ItemVendaForm(forms.ModelForm):
    produto = forms.ModelChoiceField(queryset=Produto.objects.all(), label="Produto")
    quantidade = forms.IntegerField(min_value=1, label="Quantidade")

    class Meta:
        model = ItemVenda
        fields = ['produto', 'quantidade']

    def clean_quantidade(self):
        quantidade = self.cleaned_data.get('quantidade')
        if quantidade <= 0:
            raise forms.ValidationError("A quantidade deve ser maior que zero.")
        return quantidade


class BaseItemVendaFormSet(BaseModelFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return

        produtos_usados = []
        for form in self.forms:
            if form.cleaned_data:
                produto = form.cleaned_data.get('produto')
                if produto in produtos_usados:
                    raise forms.ValidationError("Produto duplicado na venda.")
                produtos_usados.append(produto)


ItemVendaFormSet = modelformset_factory(
    ItemVenda,
    form=ItemVendaForm,
    formset=BaseItemVendaFormSet,
    extra=1,
    can_delete=True,
)
