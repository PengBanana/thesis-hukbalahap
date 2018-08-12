# Generated by Django 2.0.5 on 2018-08-08 11:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitoring', '0014_auto_20180808_1849'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='maintenanceschedule',
            name='timeAccomplished',
        ),
        migrations.AddField(
            model_name='maintenanceschedule',
            name='datetimeAccomplished',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='pool',
            name='pool_availabletimeend',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='pool',
            name='pool_availabletimestart',
            field=models.TimeField(blank=True, null=True),
        ),
    ]
