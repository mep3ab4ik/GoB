# Generated by Django 3.2.16 on 2022-10-19 08:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0069_delete_nftgenerator'),
    ]

    operations = [
        migrations.AlterField(
            model_name='card',
            name='description',
            field=models.TextField(blank=True, max_length=512, null=True),
        ),
    ]