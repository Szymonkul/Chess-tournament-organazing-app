from django import forms

from profiles.models import Profile


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = (
            'first_name', 'last_name', 'city', 'gender', 'birth_date', 'rating_fide', 'phone_number','title_or_category','club')

        labels = {
            'first_name': 'Imię',
            'last_name': 'Nazwisko',
            'birth_date': 'Data urodzenia',
            'gender': 'Płeć',
            'city': 'Miasto',
            'phone_number': 'Numer telefonu',
            'rating_fide': 'Ranking FIDE',
            'title_or_category': 'Tytuł lub kategoria',
            'club': 'Klub szachowy',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_first_name', 'required': 'required','placeholder': 'imie'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_last_name', 'required': 'required','placeholder': 'nazwisko'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_city','placeholder': 'miasto'}),
            'club': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_club', 'placeholder': 'klub'}),

            'gender': forms.Select(attrs={'class': 'form-control', 'id': 'id_gender','placeholder': 'płeć'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'id': 'id_birth_date'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_phone_number','placeholder': 'numer telefonu'}),
            'rating_fide': forms.NumberInput(attrs={'class': 'form-control', 'id': 'id_rating_fide','placeholder': 'ranking fide'}),
            'title_or_category': forms.Select(attrs={'class': 'form-control', 'id': 'id_title_or_category', 'placeholder': 'Tytuł lub kategoria'}),
        }
