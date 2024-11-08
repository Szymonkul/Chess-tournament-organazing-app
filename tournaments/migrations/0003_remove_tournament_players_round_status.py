# Generated by Django 4.1.7 on 2024-09-11 13:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournaments', '0002_alter_player_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tournament',
            name='players',
        ),
        migrations.AddField(
            model_name='round',
            name='status',
            field=models.CharField(choices=[('not_started', 'Nieutworzona'), ('in_progress', 'Utworzona'), ('completed', 'Zakończona')], default='not_started', max_length=20),
        ),
    ]
