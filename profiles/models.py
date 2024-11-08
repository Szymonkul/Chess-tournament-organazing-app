from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    GENDER_CHOICES = [('M', 'Mężczyzna'), ('F', 'Kobieta'), ]

    TITLE_AND_CATEGOREIES_CHOICES = [('GM', 'Arcymistrz'), ('IM', 'Mistrz międzynarodowy'), ('FM', 'Mistrz FIDE'),
                                     ('CM', 'Kandydat na mistrza FIDE'), ('WGM', 'Arcymistrzyni	'),
                                     ('WIM', 'Mistrzyni międzynarodowa'), ('WFM', 'Mistrzyni FIDE'),
                                     ('WCM', 'Kandydatka na mistrzynię FIDE'), ('M', 'Mistrz krajowy'),
                                     ('K', 'Kandydat na mistrza krajowego'), ('I', 'I'), ('II', 'II'),
                                     ('III', 'III'), ('IV', 'IV'), ('V', 'V'),
                                     ('Bk', 'Bk'), ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    city = models.CharField(max_length=43, blank=True, null=True)
    club = models.CharField(max_length=43, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    rating_fide = models.IntegerField(null=True, blank=True, default=1000)
    rating_pzszach = models.IntegerField(null=True, blank=True, default=1000)
    title_or_category = models.CharField(max_length=10, choices=TITLE_AND_CATEGOREIES_CHOICES, default='Bk')

    def save(self, *args, **kwargs):
        # Fide
        if self.title_or_category == 'WCM':
            self.rating_pzszach = 2000
        elif self.title_or_category == 'CM':
            self.rating_pzszach = 2200
        elif self.title_or_category == 'WFM':
            self.rating_pzszach = 2100
        elif self.title_or_category == 'FM':
            self.rating_pzszach = 2300
        elif self.title_or_category == 'WIM':
            self.rating_pzszach = 2250
        elif self.title_or_category == 'IM':
            self.rating_pzszach = 2450
        elif self.title_or_category == 'WGM':
            self.rating_pzszach = 2400
        elif self.title_or_category == 'GM':
            self.rating_pzszach = 2600
        # PZSzach
        elif self.title_or_category == 'Bk':
            self.rating_pzszach = 1000
        elif self.gender == 'M':
            if self.title_or_category == 'V':
                self.rating_pzszach = 1200
            elif self.title_or_category == 'IV':
                self.rating_pzszach = 1400
            elif self.title_or_category == 'III':
                self.rating_pzszach = 1600
            elif self.title_or_category == 'II':
                self.rating_pzszach = 1800
            elif self.title_or_category == 'I':
                self.rating_pzszach = 2000
            elif self.title_or_category == 'M':
                self.rating_pzszach = 2400
            elif self.title_or_category == 'K':
                self.rating_pzszach = 2200
        elif self.gender == 'F':
            if self.title_or_category == 'V':
                self.rating_pzszach = 1100
            elif self.title_or_category == 'IV':
                self.rating_pzszach = 1250
            elif self.title_or_category == 'III':
                self.rating_pzszach = 1400
            elif self.title_or_category == 'II':
                self.rating_pzszach = 1600
            elif self.title_or_category == 'I':
                self.rating_pzszach = 1800
            elif self.title_or_category == 'M':
                self.rating_pzszach = 2200
            elif self.title_or_category == 'K':
                self.rating_pzszach = 2000
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.user.username} Profile'
