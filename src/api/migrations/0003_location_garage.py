# Generated by Django 4.1.2 on 2022-11-20 14:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_rename_owner_garage_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='garage',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='api.garage'),
            preserve_default=False,
        ),
    ]
