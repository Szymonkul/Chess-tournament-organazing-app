# Generated by Django 4.1.7 on 2024-09-11 15:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournaments', '0003_remove_tournament_players_round_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tournament',
            name='status',
            field=models.CharField(choices=[('Nadchodzący', 'Nadchodzący'), ('Tr  wający', 'Trwający'), ('Zakończony', 'Zakończony')], max_length=12),
        ),
    ]
