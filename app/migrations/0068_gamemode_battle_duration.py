# Generated by Django 3.2.15 on 2022-10-15 11:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0067_alter_gamemode_custom_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='gamemode',
            name='battle_duration',
            field=models.IntegerField(default=3600),
        ),
    ]
