# Generated by Django 4.1.7 on 2024-09-12 17:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournaments', '0011_player_matches_count'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='player',
            name='start_category',
        ),
        migrations.AlterField(
            model_name='player',
            name='achieved_rating',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='player',
            name='avarage_oponents_rating',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='player',
            name='matches_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='player',
            name='start_rating',
            field=models.IntegerField(default=0),
        ),
    ]