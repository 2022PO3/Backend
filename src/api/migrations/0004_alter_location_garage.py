# Generated by Django 4.1.2 on 2022-11-20 14:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_location_garage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='garage',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='api.garage'),
        ),
    ]
