from django.contrib import admin

from tournaments.models import Tournament, Round, Player, Match

# Register your models here.

admin.site.register(Tournament)
admin.site.register(Round)
admin.site.register(Player)
admin.site.register(Match)


