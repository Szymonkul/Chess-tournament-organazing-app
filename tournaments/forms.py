from datetime import date

from django import forms

from tournaments.models import Tournament, Player, Match
from .models import Round, User


class TournamentForm(forms.ModelForm):
    class Meta:
        model = Tournament
        fields = ['name', 'date_begin', 'date_end', 'pace', 'arbiter', 'city', 'region', 'ranking']
        widgets = {'date_begin': forms.DateInput(attrs={'class': 'datepicker'}),
            'date_end': forms.DateInput(attrs={'type': 'date'}), }

    def clean_date_begin(self):
        date_begin = self.cleaned_data.get('date_begin')
        if date_begin and date_begin < date.today():
            raise forms.ValidationError("Data rozpoczęcia nie może być wcześniejsza niz obecna.")
        return date_begin

    def clean_date_end(self):
        date_begin = self.cleaned_data.get('date_begin')
        date_end = self.cleaned_data.get('date_end')

        if date_end and date_begin and date_end < date_begin:
            raise forms.ValidationError("Data zakończenia nie może być wcześniejsza niz data rozpoczęcia.")
        return date_end


class TournamentEditForm(forms.ModelForm):
    class Meta:
        model = Tournament
        fields = ['name', 'description','arbiter']
        widgets ={
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'arbiter': forms.Select(attrs={'class': 'form-control'}),
        }


class RemovePlayerForm(forms.Form):
    players_to_remove = forms.ModelChoiceField(queryset=Player.objects.none(), label="Usuń zawodnika")

    def __init__(self, *args, **kwargs):
        tournament = kwargs.pop('tournament')
        super().__init__(*args, **kwargs)
        self.fields['players_to_remove'].queryset = Player.objects.filter(tournament=tournament)


class MatchResultForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = ['result']  # Pole do edycji wyniku