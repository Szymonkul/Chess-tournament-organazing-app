from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.db.models import Q
from django.forms import modelformset_factory
from django.shortcuts import render, redirect, get_object_or_404
from pydantic.utils import defaultdict

from .decorators import organizer_required
from .forms import TournamentEditForm, RemovePlayerForm, TournamentForm, MatchResultForm
from .models import Tournament, Round, User, Player, Match
from django.db.models import Q
from collections import defaultdict


def add_tournament(request):
    arbiters = User.objects.filter(groups__name='Arbiter')

    if request.method == 'POST':
        form = TournamentForm(request.POST)
        if form.is_valid():
            print('dsadadadasdadmsdkomasod')
            tournament = form.save(commit=False)
            tournament.organizer = request.user
            tournament.status = 'Nadchodzący'
            tournament.save()

            if tournament.pace in ['1', '3', '5', '1+1', '3+2', '5+3']:
                tournament.type_of_tournament = 'Blyskawiczne'
            elif tournament.pace in ['10', '10+5', '15', '15+15', '10+15']:
                tournament.type_of_tournament = 'Szybkie'
            else:
                tournament.type_of_tournament = 'Klasyczne'
            return redirect('home')
        else:
            print(form.errors)
            return render(request, 'tournaments/tournament_add.html', {'form': form, 'arbiters': arbiters})

    else:
        form = TournamentForm()

    return render(request, 'tournaments/tournament_add.html', {'form': form, 'arbiters': arbiters})




def list_of_tournaments(request):
    name = request.GET.get('name', '')
    city = request.GET.get('city', '')
    region = request.GET.get('region', '')
    type_of_tournament = request.GET.get('type', '')
    status = request.GET.get('status', '')

    tournaments = Tournament.objects.filter(
        Q(status='Nadchodzący') | Q(status='Trwający')
    )

    # Dodanie filtrów na podstawie formularza wyszukiwania
    if name:
        tournaments = tournaments.filter(name__icontains=name)
    if city:
        tournaments = tournaments.filter(city__icontains=city)
    if region:
        tournaments = tournaments.filter(region__iexact=region)
    if type_of_tournament:
        tournaments = tournaments.filter(type_of_tournament__iexact=type_of_tournament)
    if status:
        tournaments = tournaments.filter(status__iexact=status)

    grouped_tournaments = defaultdict(list)
    for tournament in tournaments:
        month_name = tournament.date_begin.strftime('%B %Y')  # Formatowanie miesiąca jako "Sierpień 2024"
        grouped_tournaments[month_name].append(tournament)

    return render(request, 'tournaments/tournaments_list.html', {
        'grouped_tournaments': dict(grouped_tournaments),
        'regions': Tournament.REGION_CHOICES,
        'types': Tournament.TOURNAMENT_TYPES,
        'statuses': [("Nadchodzący","Nadchodzący"),("Trwający","Trwający")]

    })

def tournament_detail(request, tournament_id):
    tournament = Tournament.objects.get(pk=tournament_id)
    # Sprawdzenie, czy użytkownik jest już uczestnikiem turnieju
    is_signed = Player.objects.filter(tournament=tournament, user=request.user).exists()
    players = Player.objects.filter(tournament=tournament)
    # Participants statistics
    total_players = players.count()
    players_with_fide = players.filter(user__profile__rating_fide__gt=1000)
    players_with_fide_count = players_with_fide.count()
    average_fide_rating = players_with_fide.aggregate(Avg('user__profile__rating_fide'))[
        'user__profile__rating_fide__avg']
    average_pzszach_rating = players.aggregate(Avg('user__profile__rating_pzszach'))[
        'user__profile__rating_pzszach__avg']
    players = Player.objects.filter(tournament=tournament)
    rounds = Round.objects.filter(tournament=tournament)

    context = {'tournament': tournament, 'total_players': total_players,
               'players_with_fide_count': players_with_fide_count, 'average_fide_rating': average_fide_rating,
               'average_pzszach_rating': average_pzszach_rating, 'is_signed': is_signed, 'rounds': rounds,
               'players': players}

    return render(request, 'tournaments/tournament_detail.html', context)


def join_tournament(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    if request.method == 'POST':

        if tournament.status == 'Trwający' or tournament.status == 'Zakończony':
            messages.error(request, "Nie można dołączyć do turnieju, który już się rozpoczął lub został zakończony.")
            return redirect('tournament_detail', tournament_id=tournament.id)

        if tournament.add_player(request.user):
            tournament.save()
            messages.success(request, "Dołączyłeś do turnieju!")
        else:
            messages.error(request, "Już dołączyłeś do tego turnieju.")

    return redirect('tournament_detail', tournament_id=tournament.id)


@organizer_required
def edit_tournament(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    rounds = Round.objects.filter(tournament=tournament)
    players = Player.objects.filter(tournament=tournament)

    if request.method == 'POST':
        tournament_form = TournamentEditForm(request.POST, instance=tournament)
        remove_players_form = RemovePlayerForm(request.POST, tournament=tournament)
        players_to_remove = request.POST.getlist('players_to_remove')  # Pole na ID graczy do usunięcia

        # Sprawdzenie poprawności formularzy
        if tournament_form.is_valid():
            for player_id in players_to_remove:
                player = get_object_or_404(Player, id=player_id)
                player.delete()

            tournament_form.save()
            messages.success(request, "Zmiany zostały zapisane.")
            return redirect('tournament_detail', tournament_id=tournament.id)

        else:
            # Debugowanie błędów formularzy
            print(tournament_form.errors, remove_players_form.errors)
            messages.error(request, "Wystąpił błąd podczas zapisywania zmian.")

    else:
        tournament_form = TournamentEditForm(instance=tournament)
        remove_players_form = RemovePlayerForm(tournament=tournament)

    return render(request, 'tournaments/tournament_edit.html',
                  {'tournament': tournament, 'tournament_form': tournament_form,
                   'remove_players_form': remove_players_form, 'players': players})


@organizer_required
def start_tournament(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)

    if tournament.status != 'Nadchodzący':
        messages.error(request, "Turniej został już rozpoczęty lub zakończony.")
        return redirect('tournament_detail', tournament_id=tournament.id)
    elif not tournament.can_start_tournament():
        messages.error(request, "Za mała ilość graczy żeby wystartować turniej.")
        return redirect('tournament_detail', tournament_id=tournament.id)

    # Inicjalizacja turnieju
    try:
        tournament.start_tournament()
        messages.success(request, "Turniej został pomyślnie rozpoczęty!")
    except ValueError as e:
        messages.error(request, str(e))

    return redirect('tournament_detail', tournament_id=tournament.id)


@organizer_required
def enter_round_results(request, tournament_id, round_id):
    round_instance = get_object_or_404(Round, id=round_id)
    matches = Match.objects.filter(round=round_instance)
    tournament = Tournament.objects.get(id=tournament_id)

    MatchResultFormSet = modelformset_factory(Match, form=MatchResultForm, extra=0)

    if request.method == 'POST':
        formset = MatchResultFormSet(request.POST, queryset=matches)
        if formset.is_valid():
            formset.save()
            for match in matches:
                match.update_players_points(match.black_player)
                match.update_players_points(match.white_player)

            tournament.generate_round(round_number=round_instance.round_number + 1)

            return redirect('tournament_detail', tournament_id=tournament.id)
        else:
            print("Round is invalid")
            print(formset.errors)  # Wyświetl błędy formularza
    else:
        formset = MatchResultFormSet(queryset=matches)

    return render(request, 'tournaments/enter_round_results.html',
                  {'formset': formset, 'round': round_instance, 'tournament': tournament})


def round_detail(request, tournament_id, round_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    round = get_object_or_404(Round, id=round_id)
    matches = Match.objects.filter(round=round)

    return render(request, 'tournaments/round_detail.html',
                  {'round': round, 'matches': matches, 'tournament': tournament})



@login_required
def tournament_history(request):
    # Pobieramy użytkownika
    user = request.user

    # Znajdujemy turnieje, w których użytkownik brał udział i które zostały zakończone
    player_tournaments = Player.objects.filter(user=user).select_related('tournament')

    # Grupujemy turnieje według miesiąca
    grouped_tournaments = defaultdict(list)
    for player in player_tournaments:
        tournament = player.tournament
        # Klucz: Miesiąc i rok rozpoczęcia turnieju (np. "Styczeń 2023")
        month_year = tournament.date_begin.strftime('%B %Y')
        grouped_tournaments[month_year].append(tournament)

    # Sortowanie turniejów według daty rozpoczęcia (od najnowszych)
    grouped_tournaments = dict(sorted(grouped_tournaments.items(), key=lambda item: item[0], reverse=True))

    # Renderowanie szablonu
    return render(request, 'tournaments/tournament_history.html', {
        'grouped_tournaments': grouped_tournaments,
        'user': user,
    })
