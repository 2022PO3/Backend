# Generated by Django 4.1.2 on 2022-12-18 15:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_rename_unoccupied_lots_garage_entered'),
    ]

    operations = [
        migrations.AddField(
            model_name='licenceplate',
            name='entered_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='licenceplate',
            name='paid_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='reservation',
            name='showed',
            field=models.BooleanField(default=0),
            preserve_default=False,
        ),
    ]
