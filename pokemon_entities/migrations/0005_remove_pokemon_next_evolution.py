# Generated by Django 3.1.14 on 2022-07-30 17:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pokemon_entities', '0004_auto_20220730_1606'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pokemon',
            name='next_evolution',
        ),
    ]
