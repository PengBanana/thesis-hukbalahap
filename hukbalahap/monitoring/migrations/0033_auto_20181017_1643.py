# Generated by Django 2.0.5 on 2018-10-17 08:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitoring', '0032_auto_20181017_1640'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='upool',
            name='pool',
        ),
        migrations.RemoveField(
            model_name='upool',
            name='user',
        ),
        migrations.DeleteModel(
            name='uPool',
        ),
    ]