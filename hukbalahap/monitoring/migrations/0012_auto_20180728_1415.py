# Generated by Django 2.0.5 on 2018-07-28 06:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitoring', '0011_auto_20180714_0504'),
    ]

    operations = [
        migrations.AlterField(
            model_name='maintenanceschedule',
            name='act_bakingsoda',
            field=models.DecimalField(decimal_places=2, default='', max_digits=8),
        ),
        migrations.AlterField(
            model_name='maintenanceschedule',
            name='est_bakingsoda',
            field=models.DecimalField(decimal_places=2, default='', max_digits=8),
        ),
    ]
