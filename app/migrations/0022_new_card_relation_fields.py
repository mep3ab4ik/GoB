# Generated by Django 3.2.14 on 2022-07-18 13:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0021_cardhand_card_death_count'),
    ]

    operations = [
        migrations.AddField(
            model_name='cardactivemystery',
            name='clear_description',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='cardactivemystery',
            name='remove_mummy',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='carddeck',
            name='clear_description',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='carddeck',
            name='remove_mummy',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='cardgraveyard',
            name='clear_description',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='cardgraveyard',
            name='remove_mummy',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='cardhand',
            name='clear_description',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='cardhand',
            name='remove_mummy',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='control',
            name='clear_description',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='control',
            name='remove_mummy',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='tile',
            name='clear_description',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='tile',
            name='remove_mummy',
            field=models.BooleanField(default=False),
        ),
    ]
