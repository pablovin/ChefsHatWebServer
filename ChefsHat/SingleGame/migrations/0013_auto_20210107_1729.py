# Generated by Django 3.0.5 on 2021-01-07 17:29

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SingleGame', '0012_auto_20210107_1620'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dataset',
            name='playerStatus',
            field=django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(default='', max_length=500), size=None), default=list, size=None),
        ),
    ]