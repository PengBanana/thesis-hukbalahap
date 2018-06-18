# Generated by Django 2.0.5 on 2018-06-16 06:16

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Final_Ph',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('final_phlevel', models.DecimalField(decimal_places=2, default='', max_digits=5)),
                ('final_phdatetime', models.DateTimeField(blank=True, default=datetime.datetime.now)),
            ],
        ),
        migrations.CreateModel(
            name='Final_Temperature',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('final_temperaturelevel', models.DecimalField(decimal_places=2, default='', max_digits=5)),
                ('final_temperaturedatetime', models.DateTimeField(blank=True, default=datetime.datetime.now)),
            ],
        ),
        migrations.CreateModel(
            name='Final_Turbidity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('final_turbiditylevel', models.DecimalField(decimal_places=2, default='', max_digits=5)),
                ('final_turbiditydatetime', models.DateTimeField(blank=True, default=datetime.datetime.now)),
            ],
        ),
        migrations.CreateModel(
            name='MaintenanceSchedule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timeStart', models.TimeField(blank=True, null=True)),
                ('timeEnd', models.TimeField(blank=True, null=True)),
                ('timeAccomplished', models.TimeField(blank=True, null=True)),
                ('est_chlorine', models.DecimalField(decimal_places=2, default='', max_digits=8)),
                ('est_muriatic', models.DecimalField(decimal_places=2, default='', max_digits=8)),
                ('est_depowder', models.DecimalField(decimal_places=2, default='', max_digits=8)),
                ('act_chlorine', models.DecimalField(decimal_places=2, default='', max_digits=8)),
                ('act_muriatic', models.DecimalField(decimal_places=2, default='', max_digits=8)),
                ('act_depowder', models.DecimalField(decimal_places=2, default='', max_digits=8)),
            ],
        ),
        migrations.CreateModel(
            name='Pool',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pool_location', models.CharField(max_length=250)),
                ('pool_length', models.DecimalField(decimal_places=2, default='', max_digits=8)),
                ('pool_width', models.DecimalField(decimal_places=2, default='', max_digits=8)),
                ('pool_depth', models.DecimalField(decimal_places=2, default='', max_digits=8)),
            ],
        ),
        migrations.CreateModel(
            name='Temp_Ph',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('temp_phlevel', models.DecimalField(decimal_places=2, default='', max_digits=5)),
                ('temp_phdatetime', models.DateTimeField(blank=True, default=datetime.datetime.now)),
                ('pools', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='monitoring.Pool')),
            ],
        ),
        migrations.CreateModel(
            name='Temp_Temperature',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('temp_temperaturelevel', models.DecimalField(decimal_places=2, default='', max_digits=5)),
                ('temp_temperaturedatetime', models.DateTimeField(blank=True, default=datetime.datetime.now)),
                ('pools', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='monitoring.Pool')),
            ],
        ),
        migrations.CreateModel(
            name='Temp_Turbidity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('temp_turbiditylevel', models.DecimalField(decimal_places=2, default='', max_digits=5)),
                ('temp_turbiditydatetime', models.DateTimeField(blank=True, default=datetime.datetime.now)),
                ('poolID', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='monitoring.Pool')),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=45)),
                ('password', models.CharField(max_length=45)),
                ('lastname', models.CharField(max_length=45)),
                ('firstname', models.CharField(max_length=45)),
            ],
        ),
        migrations.CreateModel(
            name='Usertype_Ref',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('usertype', models.CharField(max_length=45)),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='usertype_refID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='monitoring.Usertype_Ref'),
        ),
        migrations.AddField(
            model_name='maintenanceschedule',
            name='userID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='monitoring.User'),
        ),
        migrations.AddField(
            model_name='final_turbidity',
            name='pools',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='monitoring.Pool'),
        ),
        migrations.AddField(
            model_name='final_temperature',
            name='pools',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='monitoring.Pool'),
        ),
        migrations.AddField(
            model_name='final_ph',
            name='pools',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='monitoring.Pool'),
        ),
    ]
