# Generated by Django 4.1.2 on 2023-05-16 12:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('config', '0009_imagem_garrafas'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='camera',
            name='faltantes',
        ),
        migrations.RemoveField(
            model_name='camera',
            name='garrafas',
        ),
        migrations.RemoveField(
            model_name='camera',
            name='lastValue',
        ),
        migrations.RemoveField(
            model_name='imagem',
            name='garrafas',
        ),
    ]
