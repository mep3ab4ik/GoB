# Generated by Django 3.2.14 on 2022-07-20 14:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0031_skillpointsforbattleplayer'),
    ]

    operations = [
        migrations.CreateModel(
            name='CachingTime',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                ('player_statistics', models.IntegerField(default=0)),
                ('global_statistics', models.IntegerField(default=0)),
            ],
        ),
        migrations.AlterField(
            model_name='battle',
            name='winner',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='battle_wins',
                to='app.player',
            ),
        ),
    ]
