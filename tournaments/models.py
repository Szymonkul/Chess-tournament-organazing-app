from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q


class Player(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='player')
    tournament = models.ForeignKey('Tournament', on_delete=models.CASCADE)
    points = models.FloatField(default=0)  # Punkty zdobyte przez gracza
    previous_opponents = models.ManyToManyField('self', blank=True)  # Z kim zawodnik już grał
    has_paused = models.BooleanField(default=False)
    consecutive_white_games = models.IntegerField(default=0)
    consecutive_black_games = models.IntegerField(default=0)
    last_color = models.CharField(blank=True, max_length=6)

    # variables for result table
    start_rating = models.IntegerField(default=0)
    achieved_rating = models.IntegerField(default=0)
    avarage_oponents_rating = models.IntegerField(default=0)
    matches_count = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        self.tournament.update_rounds_amount()
        super().save(*args, **kwargs)

    def calculate_achieved_rating(self):
        matches = Match.objects.filter(Q(white_player=self) | Q(black_player=self))
        total_rating = 0
        total_valid_matches = 0
        total_points = 0
        if self.tournament.ranking == 'FIDE':
            self.start_rating = self.user.profile.rating_fide
        else:
            self.start_rating = self.user.profile.rating_pzszach
        self.matches_count = matches.count()

        if matches.count() == 0:
            return 0

        for match in matches:
            opponent = match.white_player if match.black_player == self else match.black_player

            if not opponent or not hasattr(opponent, 'user') or not hasattr(opponent.user, 'profile'):
                continue
            opponent_rating = opponent.start_rating

            result = self.get_match_result(match)

            total_rating += opponent_rating
            total_valid_matches += 1

        if total_valid_matches > 0:
            total_points = self.points
            if self.has_paused:
                total_points -= 1
            average_opponent_rating = total_rating / total_valid_matches
            self.avarage_oponents_rating = average_opponent_rating
            achieved_rating = average_opponent_rating + 400 / (total_valid_matches + 1) * (
                    2 * total_points - total_valid_matches)
            print(achieved_rating)
            self.achieved_rating = achieved_rating
        else:
            achieved_rating = self.start_rating
        self.save()
        return achieved_rating

    def get_match_result(self, match):
        if match.white_player == self:
            if match.result == '1-0':
                return 1
            elif match.result == '0.5-0.5':
                return 0.5
            else:
                return 0
        elif match.black_player == self:
            if match.result == '0-1':
                return 1
            elif match.result == '0.5-0.5':
                return 0.5
            else:
                return 0

    def __str__(self):
        return f"{self.user.profile.first_name} {self.user.profile.last_name} - {self.points}"


class Tournament(models.Model):
    TOURNAMENT_TYPES = [('Błyskawiczne', 'Błyskawiczne'), ('Szybkie', 'Szybkie'), ('Klasyczne', 'Klasyczne'), ]
    PACES = [('1', '1 min'), ('3', '3 min'), ('5', '5 min'), ('10', '10 min'), ('15', '15 min'), ('30', '30 min'),
             ('60', '60 min'), ('1+1', '1+1 sec'), ('3+2', '3+2 sec'), ('5+3', '5+3 sec'), ('10+5', '10+5 sec'),
             ('10+15', '10+15 sec'), ('15+15', '15+15 sec'), ('30+10', '30+10 sec'), ('60+30', '60+30 sec'),
             ('120+30', '120+30 sec'), ]
    STATUS_CHOICES = [('Nadchodzący', 'Nadchodzący'), ('Tr  wający', 'Trwający'), ('Zakończony', 'Zakończony'), ]
    RANKING_CHOICES = [('Brak', 'Brak'), ('FIDE', 'FIDE'), ('PZSzach', 'PZSzach'), ]
    REGION_CHOICES = [('dolnośląskie', 'Dolnośląskie'), ('kujawsko-pomorskie', 'Kujawsko-pomorskie'),
                      ('lubelskie', 'Lubelskie'), ('lubuskie', 'Lubuskie'), ('łódzkie', 'Łódzkie'),
                      ('małopolskie', 'Małopolskie'), ('mazowieckie', 'Mazowieckie'), ('opolskie', 'Opolskie'),
                      ('podkarpackie', 'Podkarpackie'), ('podlaskie', 'Podlaskie'), ('pomorskie', 'Pomorskie'),
                      ('śląskie', 'Śląskie'), ('świętokrzyskie', 'Świętokrzyskie'),
                      ('warmińsko-mazurskie', 'Warmińsko-mazurskie'), ('wielkopolskie', 'Wielkopolskie'),
                      ('zachodniopomorskie', 'Zachodniopomorskie'), ]

    # Fields

    # Name
    name = models.CharField(max_length=200)
    # Dates
    date_begin = models.DateField(null=True)
    date_end = models.DateField(null=True)
    # Tournament types and similar
    pace = models.CharField(choices=PACES, max_length=10)
    type_of_tournament = models.CharField(choices=TOURNAMENT_TYPES, max_length=20)
    status = models.CharField(choices=STATUS_CHOICES, max_length=12,default='Nadchodzący')
    # Rounds
    rounds_amount = models.IntegerField(default=2)
    current_round = models.PositiveIntegerField(default=1)
    # Users
    arbiter = models.ForeignKey(User, related_name='arbited_tournaments', on_delete=models.CASCADE,blank=True, null=True)
    organizer = models.ForeignKey(User, related_name='orgianized_tournaments', on_delete=models.CASCADE)
    # Rankings
    ranking = models.CharField(choices=RANKING_CHOICES, max_length=10, default='Brak')
    # Localization
    city = models.CharField(max_length=100, null=True, blank=True)
    region = models.CharField(choices=REGION_CHOICES, max_length=100, null=True, blank=True)
    # Description
    description = models.TextField(blank=True, null=True, verbose_name='Opis turnieju')

    def update_rounds_amount(self):

        player_count = self.player_set.count()
        thresholds = [4, 6, 8, 12, 16, 24, 32, 48, 64]
        counter = 2
        for threshold in thresholds:
            if player_count >= threshold:
                counter += 1
                self.rounds_amount = counter
            else:
                break

        self.save()

    def can_start_tournament(self):
        return self.player_set.count() >= 4

    def add_player(self, user):
        player, created = Player.objects.get_or_create(user=user, tournament=self)
        return created

    def generate_round(self, round_number):
        if round_number > self.rounds_amount:
            self.calculate_rankings_for_tournament()
            self.status = "Zakończony"
            self.save()
            return

        new_round = Round.objects.create(tournament=self, round_number=round_number, status='in_progress')
        ordering_field = '-user__profile__rating_fide' if self.ranking == 'FIDE' else '-user__profile__rating_pzszach'
        players = list(Player.objects.filter(tournament=self).order_by(ordering_field))
        paused_player = None
        if len(players) % 2 != 0:
            available_for_pause = [player for player in players if not player.has_paused]
            if available_for_pause:
                available_for_pause.sort(key=lambda x: x.points+ x.start_rating/10000)
                paused_player = available_for_pause[0]

            paused_player.has_paused = True
            paused_player.points += 1
            paused_player.save()

            players.remove(paused_player)

        grouped_players = {}
        for player in players:
            points = player.points
            if points not in grouped_players:
                grouped_players[points] = []
            grouped_players[points].append(player)

        remaining_players = []
        pairs = []

        for points, group in sorted(grouped_players.items(),
                                    key=lambda x: -x[0]):
            while group:
                white_player = group.pop(0)
                found_opponent = False

                for i, black_player in enumerate(group):
                    if black_player in white_player.previous_opponents.all():
                        continue

                    if white_player.consecutive_white_games >= 2:
                        white_player, black_player = black_player, white_player
                    elif black_player.consecutive_black_games >= 2:
                        white_player, black_player = black_player, white_player

                    group.pop(i)
                    found_opponent = True
                    pairs.append((white_player, black_player))
                    break
                if not found_opponent:
                    remaining_players.append(white_player)



        while len(remaining_players) >= 2:
            white_player = remaining_players.pop(0)
            black_player = None

            for i, opponent in enumerate(remaining_players):
                if opponent not in white_player.previous_opponents.all():
                    black_player = remaining_players.pop(i)
                    break

            if black_player is None:
                black_player = remaining_players.pop(0)
                for previous_white, previous_black in reversed(pairs):
                    if black_player in previous_white.previous_opponents.all() or white_player in previous_black.previous_opponents.all():
                        previous_white, previous_black = previous_black, previous_white

                    if black_player not in previous_white.previous_opponents.all() and white_player not in previous_black.previous_opponents.all():
                        black_player, previous_black = previous_black, black_player
                        white_player, previous_white = previous_white, white_player
                        break

            pairs.append((white_player, black_player))

        for white_player, black_player in pairs:
            if white_player.consecutive_white_games >= 2:
                white_player, black_player = black_player, white_player
            elif black_player.consecutive_black_games >= 2:
                white_player, black_player = black_player, white_player

            if white_player.last_color == 'white':
                white_player.consecutive_white_games += 1
                white_player.consecutive_black_games = 0
            else:
                white_player.consecutive_white_games = 1
                white_player.consecutive_black_games = 0
            white_player.last_color = 'white'

            if black_player.last_color == 'black':
                black_player.consecutive_black_games += 1
                black_player.consecutive_white_games = 0
            else:
                black_player.consecutive_black_games = 1
                black_player.consecutive_white_games = 0
            black_player.last_color = 'black'

            white_player.previous_opponents.add(black_player)
            black_player.previous_opponents.add(white_player)
            white_player.save()
            black_player.save()
            Match.objects.create(round=new_round, white_player=white_player, black_player=black_player,
                                 table_number=new_round.matches.count() + 1)

        self.save()
        return new_round




    def start_tournament(self):
        if self.status != 'Nadchodzący':
            raise ValueError("Turniej już został rozpoczęty.")
        print('start')
        self.generate_round(round_number=1)

        self.current_round = 1
        players = Player.objects.filter(tournament=self)
        for player in players:
            if self.ranking == 'FIDE':
                player.start_rating = player.user.profile.rating_pzszach
            elif self.ranking == 'PZSzach':
                player.start_rating = player.user.profile.rating_pzszach
            player.save()
        self.status = 'Trwający'
        self.save()


    def generate_next_round(self):
        last_round = self.rounds.order_by('-round_number').first()

        if last_round and not last_round.is_completed():
            raise Exception("Nie można utworzyć nowej rundy, dopóki poprzednia nie zostanie zakończona.")

        new_round_number = last_round.round_number + 1
        self.generate_round(round_number=new_round_number)
        self.current_round = new_round_number
        self.save()


    def calculate_rankings_for_tournament(self):
        players = Player.objects.filter(tournament=self)

        for player in players:
            achieved_rating = player.calculate_achieved_rating()
            player.achieved_rating = achieved_rating

            if self.ranking == 'FIDE':
                player.user.profile.rating_fide = achieved_rating
            elif self.ranking == 'PZSzach':
                player.achieved_rating = self.calculate_category(achieved_rating, player.user.profile)


    @staticmethod
    def calculate_category(result, profile):
        if profile.title_or_category in ['GM', 'WGM', 'IM', 'WIM', 'FM', 'WFM', 'CM',
                                         'WCM'] or profile.rating_pzszach >= result:
            return
        category = 'Bk'
        if profile.gender == 'M':
            if result >= 2400:
                category = 'M'
            elif result >= 2200:
                category = 'K'
            elif result >= 2000:
                category = 'I'
            elif result >= 1800:
                category = 'II'
            elif result >= 1550:
                category = 'III'
            elif result >= 1300:
                category = 'IV'
            elif result >= 1050:
                category = 'V'
        elif profile.gender == 'F':
            if result >= 2200:
                category = 'M'
            elif result >= 2000:
                category = 'K'
            elif result >= 1800:
                category = 'I'
            elif result >= 1600:
                category = 'II'
            elif result >= 1350:
                category = 'III'
            elif result >= 1150:
                category = 'IV'
            elif result >= 1000:
                category = 'V'

        return category


class Round(models.Model):
    tournament = models.ForeignKey('Tournament', on_delete=models.CASCADE, related_name='rounds')
    round_number = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=[('not_started', 'Nieutworzona'), ('in_progress', 'Utworzona'),
                                                      ('completed', 'Zakończona')], default='not_started')

    class Meta:
        ordering = ['round_number']
        unique_together = ('tournament', 'round_number')
        verbose_name = 'Runda'
        verbose_name_plural = 'Rundy'

    def __str__(self):
        return f'Runda {self.round_number} - {self.tournament.name}'


class Match(models.Model):
    round = models.ForeignKey('Round', on_delete=models.CASCADE, related_name='matches')
    white_player = models.ForeignKey(Player, related_name='white_matches', on_delete=models.CASCADE)
    black_player = models.ForeignKey(Player, related_name='black_matches', on_delete=models.CASCADE)
    result = models.CharField(max_length=10, choices=[('1-0', '1-0'), ('0-1', '0-1'), ('0.5-0.5', '0.5-0.5')],
                              blank=True)
    table_number = models.PositiveIntegerField()

    def __str__(self):
        return f"Table {self.table_number}: {self.white_player} vs {self.black_player}"

    def update_players_points(self, player):
        if self.white_player == player:
            if self.result == '1-0':
                self.white_player.points += 1
            elif self.result == '0.5-0.5':
                self.white_player.points += 0.5
        else:
            if self.result == '0-1':
                self.black_player.points += 1
            elif self.result == '0.5-0.5':
                self.black_player.points += 0.5

        self.white_player.save()
        self.black_player.save()

        self.white_player.previous_opponents.add(self.black_player)
        self.black_player.previous_opponents.add(self.white_player)
