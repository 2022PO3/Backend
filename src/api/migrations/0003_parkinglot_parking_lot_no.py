# Generated by Django 4.1.2 on 2022-11-23 07:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_alter_image_table'),
    ]

    operations = [
        migrations.AddField(
            model_name='parkinglot',
            name='parking_lot_no',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
