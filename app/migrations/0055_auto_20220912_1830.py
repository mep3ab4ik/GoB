# Generated by Django 3.2.15 on 2022-09-12 18:30

from django.db import migrations, models
import django.db.models.deletion


def remove_player_statuses(apps, schema_editor):
    Player = apps.get_model('app', 'Player')
    Player.objects.update(status=None)
    PlayerStatus = apps.get_model('app', 'PlayerStatus')
    PlayerStatus.objects.create(title='AFK', name='away')



class Migration(migrations.Migration):
    dependencies = [
        ('app', '0054_cards_history_changes'),
    ]

    operations = [
        migrations.CreateModel(
            name='PlayerStatus',
            fields=[
                ('name', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=64)),
            ],
        ),
        migrations.AlterField(
            model_name='player',
            name='status',
            field=models.CharField(blank=True, null=True, max_length=50),
        ),
        migrations.RunPython(remove_player_statuses),
        migrations.AlterField(
            model_name='player',
            name='status',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                                    to='app.playerstatus'),
        ),
    ]
