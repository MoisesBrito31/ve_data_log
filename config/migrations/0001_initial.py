# Generated by Django 3.1.7 on 2021-03-17 11:14

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Camera',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('criado', models.DateTimeField(auto_now_add=True, verbose_name='Criado')),
                ('modificado', models.DateTimeField(auto_now=True, verbose_name='Modificado')),
                ('ativo', models.BooleanField(default=True, verbose_name='Ativo?')),
                ('nome', models.CharField(max_length=50, verbose_name='nome')),
                ('porta', models.IntegerField(verbose_name='porta')),
                ('ip', models.IntegerField(unique=True, verbose_name='ip')),
                ('status', models.CharField(max_length=15, verbose_name='status')),
            ],
            options={
                'verbose_name': 'Câmera',
                'verbose_name_plural': 'Câmeras',
            },
        ),
    ]
