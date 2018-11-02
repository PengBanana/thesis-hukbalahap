# Generated by Django 2.0.5 on 2018-11-02 17:47

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Chemical_Price_Reference',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chemical', models.TextField()),
                ('quantity', models.DecimalField(decimal_places=2, default='', max_digits=8)),
                ('price', models.DecimalField(decimal_places=2, default='', max_digits=8)),
                ('effectiveDate', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Chlorine_Effectiveness',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ce_datettime', models.DateTimeField(blank=True, default=datetime.datetime.now)),
                ('ce_percentage', models.DecimalField(decimal_places=2, default='', max_digits=5)),
            ],
        ),
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
                ('date', models.DateField(default='2018-11-03', null=True)),
                ('estimatedStart', models.DateTimeField(blank=True, null=True)),
                ('estimatedEnd', models.DateTimeField(blank=True, null=True)),
                ('scheduledStart', models.DateTimeField(blank=True, null=True)),
                ('scheduledEnd', models.DateTimeField(blank=True, null=True)),
                ('datetimeAccomplished', models.DateTimeField(blank=True, null=True)),
                ('est_chlorine', models.DecimalField(decimal_places=2, default=None, max_digits=8, null=True)),
                ('est_muriatic', models.DecimalField(decimal_places=2, default=None, max_digits=8)),
                ('est_depowder', models.DecimalField(decimal_places=2, default=None, max_digits=8)),
                ('est_bakingsoda', models.DecimalField(decimal_places=2, default=None, max_digits=8)),
                ('act_chlorine', models.DecimalField(decimal_places=2, default=None, max_digits=8, null=True)),
                ('act_muriatic', models.DecimalField(decimal_places=2, default=None, max_digits=8)),
                ('act_depowder', models.DecimalField(decimal_places=2, default=None, max_digits=8)),
                ('act_bakingsoda', models.DecimalField(decimal_places=2, default=None, max_digits=8)),
                ('status', models.TextField(default='Scheduled')),
            ],
        ),
        migrations.CreateModel(
            name='MobileNumber',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mobileNumber', models.CharField(blank=True, default=None, max_length=13, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Notification_Table',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('number', models.IntegerField(null=True)),
                ('type', models.TextField(default='Pool Technician')),
                ('date', models.DateField(default='2018-11-03', null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Pool',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pool_location', models.CharField(default='', max_length=250)),
                ('pool_name', models.CharField(default='', max_length=250)),
                ('pool_length', models.DecimalField(decimal_places=2, default='', max_digits=8)),
                ('pool_width', models.DecimalField(decimal_places=2, default='', max_digits=8)),
                ('pool_depth', models.DecimalField(decimal_places=2, default='', max_digits=8)),
                ('pool_availabletimestart', models.TimeField(blank=True, null=True)),
                ('pool_availabletimeend', models.TimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Status',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Status_Ref',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status_ref', models.CharField(max_length=45)),
            ],
        ),
        migrations.CreateModel(
            name='Temp_Ph',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('temp_phlevel', models.DecimalField(decimal_places=2, default='', max_digits=5)),
                ('temp_phdatetime', models.DateTimeField(blank=True, default=datetime.datetime.now)),
                ('pool', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='monitoring.Pool')),
            ],
        ),
        migrations.CreateModel(
            name='Temp_Temperature',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('temp_temperaturelevel', models.DecimalField(decimal_places=2, default='', max_digits=5)),
                ('temp_temperaturedatetime', models.DateTimeField(blank=True, default=datetime.datetime.now)),
                ('pool', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='monitoring.Pool')),
            ],
        ),
        migrations.CreateModel(
            name='Temp_Turbidity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('temp_turbiditylevel', models.DecimalField(decimal_places=2, default='', max_digits=5)),
                ('temp_turbiditydatetime', models.DateTimeField(blank=True, default=datetime.datetime.now)),
                ('pool', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='monitoring.Pool')),
            ],
        ),
        migrations.CreateModel(
            name='Type',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='uPool',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pool', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='monitoring.Pool')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
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
            model_name='type',
            name='type',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE, to='monitoring.Usertype_Ref'),
        ),
        migrations.AddField(
            model_name='type',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='status',
            name='status',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='monitoring.Status_Ref'),
        ),
        migrations.AddField(
            model_name='status',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='maintenanceschedule',
            name='pool',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='monitoring.Pool'),
        ),
        migrations.AddField(
            model_name='maintenanceschedule',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='final_turbidity',
            name='pool',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='monitoring.Pool'),
        ),
        migrations.AddField(
            model_name='final_temperature',
            name='pool',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='monitoring.Pool'),
        ),
        migrations.AddField(
            model_name='final_ph',
            name='pool',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='monitoring.Pool'),
        ),
        migrations.AddField(
            model_name='chlorine_effectiveness',
            name='pool',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='monitoring.Pool'),
        ),
    ]
