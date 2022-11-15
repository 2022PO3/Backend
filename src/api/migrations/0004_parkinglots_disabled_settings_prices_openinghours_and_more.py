# Generated by Django 4.1.2 on 2022-11-15 10:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0003_remove_licenceplates_entered_at_licenceplates_garage_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='parkinglots',
            name='disabled',
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name='Settings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('location', models.CharField(choices=[(None, '(UNK)'), ('ANT', 'Antwerpen'), ('HAI', 'Henegouwen'), ('LIE', 'Luik'), ('LIM', 'Limburg'), ('LUX', 'Luxemburg'), ('NAM', 'Namen'), ('OVL', 'Oost-Vlaanderen'), ('WVL', 'West-Vlaanderen'), ('VBR', 'Vlaams-Brabant'), ('WBR', 'Waals-Brabant')], default='(UNK)', max_length=3)),
                ('fav_garage_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.garages')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Prices',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('price_string', models.CharField(max_length=192)),
                ('price', models.FloatField()),
                ('valuta', models.CharField(choices=[('EUR', 'Euro'), ('USD', 'Dollar'), ('GBP', 'Pound')], default='EUR', max_length=3)),
                ('garage_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.garages')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OpeningHours',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('day_from', models.IntegerField(choices=[(0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'), (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday')])),
                ('day_to', models.IntegerField(choices=[(0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'), (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday')])),
                ('hour_from', models.DateTimeField()),
                ('hour_to', models.DateTimeField()),
                ('garage_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.garages')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Locations',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('country', models.CharField(max_length=192)),
                ('province', models.CharField(choices=[(None, '(UNK)'), ('ANT', 'Antwerpen'), ('HAI', 'Henegouwen'), ('LIE', 'Luik'), ('LIM', 'Limburg'), ('LUX', 'Luxemburg'), ('NAM', 'Namen'), ('OVL', 'Oost-Vlaanderen'), ('WVL', 'West-Vlaanderen'), ('VBR', 'Vlaams-Brabant'), ('WBR', 'Waals-Brabant')], max_length=3)),
                ('municipality', models.CharField(max_length=192)),
                ('post_code', models.IntegerField()),
                ('street', models.CharField(max_length=192)),
                ('number', models.IntegerField()),
                ('garage_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.garages')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='GarageSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('max_height', models.FloatField()),
                ('max_width', models.FloatField()),
                ('max_handicapped_lots', models.IntegerField()),
                ('garage_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.garages')),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.locations')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
