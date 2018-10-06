# Generated by Django 2.0.5 on 2018-10-06 07:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('monitoring', '0019_auto_20180811_0500'),
    ]

    operations = [
        migrations.CreateModel(
            name='Chemical_Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chemicalName', models.TextField()),
                ('chemicalUsageLimit', models.IntegerField()),
                ('chemicalDescription', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Chemical_Price_Reference',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('effectiveDate', models.DateField()),
                ('price', models.DecimalField(decimal_places=2, default='', max_digits=8)),
                ('chemical', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='monitoring.Chemical_Item')),
            ],
        ),
        migrations.CreateModel(
            name='Chemical_Usage_Log',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('usageDate', models.DateField()),
                ('quantity', models.IntegerField()),
                ('chemical', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='monitoring.Chemical_Item')),
                ('pool', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='monitoring.Pool')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterField(
            model_name='maintenanceschedule',
            name='date',
            field=models.DateField(default='2018-10-06', null=True),
        ),
        migrations.AlterField(
            model_name='maintenanceschedule',
            name='status',
            field=models.TextField(default='Scheduled'),
        ),
        migrations.AlterField(
            model_name='notification_table',
            name='date',
            field=models.DateField(default='2018-10-06', null=True),
        ),
        migrations.AlterField(
            model_name='type',
            name='type',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE, to='monitoring.Usertype_Ref'),
        ),
    ]
