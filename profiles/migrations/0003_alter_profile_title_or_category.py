# Generated by Django 4.1.7 on 2024-09-12 00:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0002_alter_profile_gender_alter_profile_title_or_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='title_or_category',
            field=models.CharField(choices=[('GM', 'Arcymistrz'), ('IM', 'Mistrz międzynarodowy'), ('FM', 'Mistrz FIDE'), ('CM', 'Kandydat na mistrza FIDE'), ('WGM', 'Arcymistrzyni\t'), ('WIM', 'Mistrzyni międzynarodowa'), ('WFM', 'Mistrzyni FIDE'), ('WCM', 'Kandydatka na mistrzynię FIDE'), ('M', 'Mistrz krajowy'), ('K', 'Kandydat na mistrza krajowego'), ('I', 'I'), ('II', 'II'), ('III', 'III'), ('IV', 'IV'), ('V', 'V'), ('Bk', 'Bk')], default='Bk', max_length=10),
        ),
    ]