# Generated by Django 4.1.7 on 2024-09-12 20:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournaments', '0012_remove_player_start_category_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='has_paused',
            field=models.BooleanField(default=False),
        ),
    ]
