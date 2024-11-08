from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SignUp_form(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput({'placeholder': 'Podaj Nazwę użytkownika', }))
    email = forms.CharField(widget=forms.TextInput({'placeholder': 'Podaj Email', }))
    password1 = forms.CharField(widget=forms.PasswordInput({'placeholder': 'Podaj hasło', }))
    password2 = forms.CharField(widget=forms.PasswordInput({'placeholder': 'Powtórz hasło', }))

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'email')
