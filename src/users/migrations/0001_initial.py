# Generated by Django 4.1.2 on 2022-12-14 15:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('first_name', models.CharField(max_length=192, null=True)),
                ('last_name', models.CharField(max_length=192, null=True)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('role', models.IntegerField(choices=[(0, 'Generated User'), (1, 'Normal User'), (2, 'Garage Owner'), (3, 'Admin')])),
                ('is_active', models.BooleanField(default=True)),
                ('two_factor', models.BooleanField(default=False)),
                ('two_factor_validated', models.BooleanField(blank=True, null=True)),
                ('location', models.CharField(choices=[(None, 'UNK'), ('ANT', 'Antwerpen'), ('HAI', 'Henegouwen'), ('LIE', 'Luik'), ('LIM', 'Limburg'), ('LUX', 'Luxemburg'), ('NAM', 'Namen'), ('OVL', 'Oost-Vlaanderen'), ('WVL', 'West-Vlaanderen'), ('VBR', 'Vlaams-Brabant'), ('WBR', 'Waals-Brabant')], max_length=3, null=True)),
                ('stripe_identifier', models.CharField(max_length=18, null=True)),
                ('fav_garage', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='fav_garage', to='api.garage')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
