# Generated by Django 3.2.12 on 2022-06-30 10:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0015_alter_card_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='gamemode',
            name='default_game_mode',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='card',
            name='description',
            field=models.TextField(
                blank=True,
                help_text='You can provide keywords, list:<br><br>Last Breath, Warcry, Insult, Barrier, Invisible, Pounce, Ensnare, Ensnared, MIA, Mummy, Untouchable, Apocalype, Censor, Aqua, Dig, Burn, Shock, Mystery, Lethal, Apocalypse, Leech, Censored, Warcries, Mysteries, Water Upgrade, Earth Upgrade, Electricity Upgrade, Fire Upgrade, Fire Tile Upgrade, Electricity Tile Upgrade, Earth Tile Upgrade, Water Tile Upgrade',
                max_length=512,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name='gamemode',
            name='ends_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]