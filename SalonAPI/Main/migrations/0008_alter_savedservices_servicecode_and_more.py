# Generated by Django 5.2.3 on 2025-07-17 20:15

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Main', '0007_savedservices_servicecode_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='savedservices',
            name='ServiceCode',
            field=models.CharField(default='Huh', max_length=20),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='savedservices',
            name='UserID',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='saved_services', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='services',
            name='AppID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Services', to='Main.appointments'),
        ),
        migrations.AlterField(
            model_name='services',
            name='ServiceCode',
            field=models.CharField(default='Hey', max_length=20),
            preserve_default=False,
        ),
    ]
