from django import forms
from django.contrib.auth.models import User

class UserForm(forms.ModelForm):
    first_name = forms.CharField(label='Nome', max_length=150)
    last_name = forms.CharField(label='Sobrenome', max_length=150)
    email = forms.EmailField(label='Email')
    password = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput,
        required=False,  # senha opcional para edição
    )
    password_confirm = forms.CharField(
        label="Confirme a senha",
        widget=forms.PasswordInput,
        required=False,  # confirmação opcional para edição
    )

    class Meta:
        model = User
        fields = ['first_name', 
                  'last_name', 
                  'email', 
                  'password'
                  ]

    def clean(self):
        cleaned_data = super().clean()
        senha = cleaned_data.get("password")
        senha_confirm = cleaned_data.get("password_confirm")

        # Se algum dos dois foi preenchido, validar igualdade
        if senha or senha_confirm:
            if senha != senha_confirm:
                raise forms.ValidationError("As senhas não conferem.")
        return cleaned_data
