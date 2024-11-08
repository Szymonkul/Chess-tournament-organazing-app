from datetime import timedelta, date
from django.contrib.auth.models import User, Group
from django.test import TestCase, Client

from profiles.models import Profile
from .models import Player, Tournament, Match, Round


class PlayerTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='testuser1', password='12345')

        self.tournament = Tournament.objects.create(name='Test Tournament', ranking='FIDE', pace='60',
                                                    type_of_tournament='Klasyczne', organizer=self.user, )
        self.player = Player.objects.create(user=self.user, tournament=self.tournament, start_rating=1540, points=1.5)
        self.user1 = User.objects.create(username='testuser2', password='12345')
        self.user2 = User.objects.create(username='testuser3', password='12345')
        self.profile = Profile.objects.create(user=self.user, rating_fide=1540, rating_pzszach=1600)
        self.profile1 = Profile.objects.create(user=self.user1, rating_fide=1500,
                                               rating_pzszach=1500)  # Przykładowe wartości ratingu
        self.profile2 = Profile.objects.create(user=self.user2, rating_fide=1600, rating_pzszach=1700)

    def test_calculate_achieved_rating(self):
        opponent1 = Player.objects.create(user=self.user1, tournament=self.tournament, start_rating=1500)
        opponent2 = Player.objects.create(user=self.user2, tournament=self.tournament, start_rating=1600)

        Match.objects.create(white_player=self.player, black_player=opponent1, result='1-0', table_number=1,
                             round=Round.objects.create(tournament=self.tournament, round_number=1))
        Match.objects.create(white_player=self.player, black_player=opponent2, result='1-0', table_number=2,
                             round=Round.objects.create(tournament=self.tournament, round_number=2))

        achieved_rating = self.player.calculate_achieved_rating()
        estimate_rank = (opponent1.start_rating + opponent2.start_rating) / 2 + 400 / 3 * (self.player.points * 2 - 2)
        self.assertEqual(achieved_rating, estimate_rank)
        print(achieved_rating, estimate_rank)

    def test_calculate_achieved_rating_with_pause(self):
        self.player.has_paused = True
        self.player.points = 2
        self.player.save()

        opponent1 = Player.objects.create(user=self.user1, tournament=self.tournament, start_rating=1500)
        Match.objects.create(white_player=self.player, black_player=opponent1, result='1-0', table_number=1,
                             round=Round.objects.create(tournament=self.tournament, round_number=1))

        achieved_rating = self.player.calculate_achieved_rating()
        print(achieved_rating)
        self.assertEqual(achieved_rating, 1700)


class TournamentRoundGenerationTest(TestCase):

    def setUp(self):
        # Tworzymy użytkowników
        self.user1 = User.objects.create(username='user1', password='<PASSWORD>')
        self.user2 = User.objects.create(username='user2', password='<PASSWORD>')
        self.user3 = User.objects.create(username='user3', password='<PASSWORD>')
        self.user4 = User.objects.create(username='user4', password='<PASSWORD>')
        self.user5 = User.objects.create(username='user5', password='<PASSWORD>')
        self.user6 = User.objects.create(username='user6', password='<PASSWORD>')

        self.profile1 = Profile.objects.create(user=self.user1, rating_fide=1500, rating_pzszach=1500)
        self.profile2 = Profile.objects.create(user=self.user2, rating_fide=1540, rating_pzszach=1500)
        self.profile3 = Profile.objects.create(user=self.user3, rating_fide=1560, rating_pzszach=1500)
        self.profile4 = Profile.objects.create(user=self.user4, rating_fide=1580, rating_pzszach=1500)
        self.profile5 = Profile.objects.create(user=self.user5, rating_fide=1600, rating_pzszach=1500)
        self.profile6 = Profile.objects.create(user=self.user6, rating_fide=1700, rating_pzszach=1500)
        # Tworzymy turniej
        self.tournament = Tournament.objects.create(name='Test Tournament', ranking='FIDE', pace='60',
                                                    type_of_tournament='Klasyczne', organizer=self.user1,
                                                    status="Nadchodzący")
        # Dodajemy graczy do turnieju
        self.player1 = Player.objects.create(user=self.user1, tournament=self.tournament, start_rating=1500)
        self.player2 = Player.objects.create(user=self.user2, tournament=self.tournament, start_rating=1540)
        self.player3 = Player.objects.create(user=self.user3, tournament=self.tournament, start_rating=1580)
        self.player4 = Player.objects.create(user=self.user4, tournament=self.tournament, start_rating=1600)
        self.player5 = Player.objects.create(user=self.user5, tournament=self.tournament, start_rating=1750)

    def test_generate_first_round_with_even_players(self):
        self.player6 = Player.objects.create(user=self.user6, tournament=self.tournament, start_rating=1800)

        # Test z parzystą liczbą graczy (bez pauzy)
        self.tournament.start_tournament()

        # Sprawdzamy, czy zostały utworzone mecze
        matches = self.tournament.rounds.get(round_number=1).matches.all()
        self.assertEqual(matches.count(), 3)  # 6 gracze, 3 mecze
        players_sorted_by_rating = sorted(
            [self.player1, self.player2, self.player3, self.player4, self.player5, self.player6],
            key=lambda p: p.start_rating, reverse=True)

        # Sprawdzenie, czy gracze zostali poprawnie sparowani (1 z 2, 3 z 4, itd.)
        expected_pairs = [(players_sorted_by_rating[0], players_sorted_by_rating[1]),  # Gracz 1 z Graczem 2
            (players_sorted_by_rating[2], players_sorted_by_rating[3]),  # Gracz 3 z Graczem 4
            (players_sorted_by_rating[4], players_sorted_by_rating[5])  # Gracz 5 z Graczem 6
        ]

        for match, (expected_white, expected_black) in zip(matches, expected_pairs):
            print(match.white_player.user.username, expected_white.user.username, match.black_player.user.username,
                  expected_black.user.username)

            self.assertEqual(match.white_player, expected_white),
            self.assertEqual(match.black_player, expected_black)

    def test_generate_first_round_with_odd_players(self):
        # Test z nieparzystą liczbą graczy (z pauzą)
        self.tournament.start_tournament()

        # Sprawdzamy, czy zostały utworzone mecze
        matches = self.tournament.rounds.get().matches.all()
        # Sprawdzamy, czy jeden gracz pauzuje
        paused_player = Player.objects.get(has_paused=True)
        self.assertEqual(paused_player.points, 1)

        players_sorted_by_rating = sorted([self.player1, self.player2, self.player3, self.player4, self.player5],
                                          key=lambda p: p.start_rating,reverse=True)

        # Sprawdzenie, czy gracze zostali poprawnie sparowani
        expected_pairs = [(players_sorted_by_rating[0], players_sorted_by_rating[1]),  # Gracz 1 z Graczem 2
                          (players_sorted_by_rating[2], players_sorted_by_rating[3])  # Gracz 3 z Graczem 4
                          ]
        for match, (expected_white, expected_black) in zip(matches, expected_pairs):
            print(match.white_player.user.username, expected_white.user.username, match.black_player.user.username,
                  expected_black.user.username)

            self.assertEqual(match.white_player, expected_white)
            self.assertEqual(match.black_player, expected_black)

        self.assertEqual(paused_player, players_sorted_by_rating[4])

    def test_generate_multiple_rounds(self):
        # Wygeneruj pierwszą rundę
        self.tournament.generate_round(round_number=1)

        # Wygeneruj drugą rundę
        self.tournament.generate_round(round_number=2)

        # Sprawdź, czy druga runda nie ma par graczy, którzy już ze sobą grali
        first_round_matches = self.tournament.rounds.get(round_number=1).matches.all()
        second_round_matches = self.tournament.rounds.get(round_number=2).matches.all()

        first_round_pairs = set([(match.white_player, match.black_player) for match in first_round_matches])
        second_round_pairs = set([(match.white_player, match.black_player) for match in second_round_matches])

        for pair in second_round_pairs:
            self.assertNotIn(pair, first_round_pairs)

class TournamentFunctionalTest(TestCase):
    def setUp(self):
        self.client = Client()

        # Tworzenie użytkownika i przypisanie do grupy "organizer
        self.organizer_group, created = Group.objects.get_or_create(name='Organizer')

        self.user = User.objects.create_user(username='testuser', password='12345')
        self.organizer_group.user_set.add(self.user)
        self.profile = Profile.objects.create(user=self.user, rating_fide=1600, rating_pzszach=1500)

        # Logowanie użytkownika
        self.client.login(username='testuser', password='12345')

    def test_full_tournament_flow(self):
        # Krok 1: Tworzenie turnieju przez użytkownika
        begin_date = date.today() + timedelta(days=1)
        end_date = date.today() + timedelta(days=2)

        response = self.client.post('/tournaments/add/', {
            'name': 'Test Tournament',
            'ranking': 'FIDE',
            'pace': '60',
            'type_of_tournament': 'Klasyczne',
            'organizer': self.user.id,
            'date_begin': begin_date,
            'date_end': end_date,
            'city': "Katowice",
            'region': 'opolskie',
        })
        self.assertEqual(response.status_code, 302)

        # Pobranie stworzonego turnieju
        tournament = Tournament.objects.get(name='Test Tournament')

        # Krok 2: Dodanie graczy do turnieju
        players_data = [
            {'username': 'player1', 'rating_fide': 1500},
            {'username': 'player2', 'rating_fide': 1550},
            {'username': 'player3', 'rating_fide': 1600},
            {'username': 'player4', 'rating_fide': 1650},
        ]
        for player_data in players_data:
            user = User.objects.create_user(username=player_data['username'], password='12345')
            Profile.objects.create(user=user, rating_fide=player_data['rating_fide'], rating_pzszach=1500)
            Player.objects.create(user=user, tournament=tournament, start_rating=player_data['rating_fide'])

        # Krok 3: Wygenerowanie pierwszej rundy
        response = self.client.post(f'/tournaments/{tournament.id}/start/')
        self.assertEqual(response.status_code, 302)  # Sprawdzenie, czy turniej wystartował

        # Pobranie pierwszej rundy i jej meczów
        round1 = Round.objects.get(tournament=tournament, round_number=1)
        matches = round1.matches.all()
        self.assertEqual(matches.count(), 2)  # Powinny być dwa mecze (4 graczy)

        # Krok 4: Zgłaszanie wyników meczów przez stronę z rundą
        form_data = {
            'form-TOTAL_FORMS': matches.count(),  # Liczba formularzy w formsecie
            'form-INITIAL_FORMS': matches.count(),  # Liczba początkowych formularzy
        }

        # Dodanie wyników dla każdego meczu
        for i, match in enumerate(matches):
            form_data[f'form-{i}-id'] = match.id
            form_data[f'form-{i}-result'] = '1-0'  # Gracz biały wygrywa

        # Przesłanie danych formsetu
        response = self.client.post(f'/tournaments/{tournament.id}/round/{round1.id}/edit/', form_data)
        self.assertEqual(response.status_code, 302)  # Sprawdzenie, czy wynik został zapisany

        # Sprawdzenie, czy wyniki zostały zaktualizowane
        for match in matches:
            match.refresh_from_db()
            self.assertEqual(match.result, '1-0')  # Każdy mecz powinien mieć wynik '1-0'


        # Sprawdzenie, czy wygenerowano drugą rundę
        round2 = Round.objects.get(tournament=tournament, round_number=2)
        self.assertIsNotNone(round2)

        # Sprawdzenie, czy żadni gracze nie zostali sparowani ponownie w tej samej parze
        round1_pairs = set([(m.white_player, m.black_player) for m in round1.matches.all()])
        round2_pairs = set([(m.white_player, m.black_player) for m in round2.matches.all()])

        for pair in round2_pairs:
            self.assertNotIn(pair, round1_pairs)  # Sprawdzenie, że pary w drugiej rundzie są inne