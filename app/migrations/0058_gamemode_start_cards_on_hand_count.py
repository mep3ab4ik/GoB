# Generated by Django 3.2.15 on 2022-09-27 09:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0057_auto_20220923_2202'),
    ]

    operations = [
        migrations.AddField(
            model_name='gamemode',
            name='start_cards_on_hand_count',
            field=models.IntegerField(default=5),
        ),
    ]
