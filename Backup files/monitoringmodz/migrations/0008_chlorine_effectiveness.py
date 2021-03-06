# Generated by Django 2.0.5 on 2018-07-09 08:20

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('monitoring', '0007_maintenanceschedule_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='Chlorine_Effectiveness',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ce_datettime', models.DateTimeField(blank=True, default=datetime.datetime.now)),
                ('ce_percentage', models.DecimalField(decimal_places=2, default='', max_digits=5)),
                ('pool', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='monitoring.Pool')),
            ],
        ),
    ]
