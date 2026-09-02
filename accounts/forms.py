from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password


class RegisterForm(forms.ModelForm):

    password = forms.CharField(
        widget=forms.PasswordInput,
        label="Senha"
    )

    password_confirm = forms.CharField(
        widget=forms.PasswordInput,
        label="Confirmar senha"
    )

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "password",
        )

    def clean(self):

        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm:

            if password != password_confirm:
                raise forms.ValidationError(
                    "As senhas não coincidem."
                )

            validate_password(password)
            
        return cleaned_data