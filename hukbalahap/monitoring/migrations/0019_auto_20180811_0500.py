# Generated by Django 2.0.5 on 2018-08-10 21:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitoring', '0018_merge_20180811_0500'),
    ]

    operations = [
        migrations.AlterField(
            model_name='maintenanceschedule',
            name='date',
            field=models.DateField(default='2018-08-11', null=True),
        ),
    ]