# Generated by Django 3.2.14 on 2022-08-10 09:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0038_alter_playerseasonstats_skill_level'),
    ]

    operations = [
        migrations.AlterField(
            model_name='skillpointsladder',
            name='game_mode',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='game_mode_ladder', to='app.gamemode'),
        ),
    ]