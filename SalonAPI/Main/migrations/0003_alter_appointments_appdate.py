# Generated by Django 5.2.3 on 2025-07-01 01:56

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Main', '0002_services_servicestarttime'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointments',
            name='AppDate',
            field=models.DateField(default=datetime.date.today),
        ),
    ]
