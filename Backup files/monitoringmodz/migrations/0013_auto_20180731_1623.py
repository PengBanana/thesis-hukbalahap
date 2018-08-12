# Generated by Django 2.0.5 on 2018-07-31 08:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitoring', '0012_auto_20180728_1415'),
    ]

    operations = [
        migrations.AlterField(
            model_name='maintenanceschedule',
            name='act_bakingsoda',
            field=models.DecimalField(decimal_places=2, default=None, max_digits=8),
        ),
        migrations.AlterField(
            model_name='maintenanceschedule',
            name='act_chlorine',
            field=models.DecimalField(decimal_places=2, default=None, max_digits=8, null=True),
        ),
        migrations.AlterField(
            model_name='maintenanceschedule',
            name='act_depowder',
            field=models.DecimalField(decimal_places=2, default=None, max_digits=8),
        ),
        migrations.AlterField(
            model_name='maintenanceschedule',
            name='act_muriatic',
            field=models.DecimalField(decimal_places=2, default=None, max_digits=8),
        ),
        migrations.AlterField(
            model_name='maintenanceschedule',
            name='date',
            field=models.DateField(default='2018-07-31', null=True),
        ),
        migrations.AlterField(
            model_name='maintenanceschedule',
            name='est_bakingsoda',
            field=models.DecimalField(decimal_places=2, default=None, max_digits=8),
        ),
        migrations.AlterField(
            model_name='maintenanceschedule',
            name='est_chlorine',
            field=models.DecimalField(decimal_places=2, default=None, max_digits=8, null=True),
        ),
        migrations.AlterField(
            model_name='maintenanceschedule',
            name='est_depowder',
            field=models.DecimalField(decimal_places=2, default=None, max_digits=8),
        ),
        migrations.AlterField(
            model_name='maintenanceschedule',
            name='est_muriatic',
            field=models.DecimalField(decimal_places=2, default=None, max_digits=8),
        ),
        migrations.AlterField(
            model_name='maintenanceschedule',
            name='estimatedEnd',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='maintenanceschedule',
            name='estimatedStart',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='maintenanceschedule',
            name='scheduledEnd',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='maintenanceschedule',
            name='scheduledStart',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]