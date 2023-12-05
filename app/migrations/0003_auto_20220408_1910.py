# Generated by Django 3.2.7 on 2022-04-08 19:10

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_trace'),
    ]

    operations = [
        migrations.RenameField(
            model_name='trace',
            old_name='created_date',
            new_name='first_time_triggered',
        ),
        migrations.AddField(
            model_name='trace',
            name='count_triggered',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='trace',
            name='last_time_triggered',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
