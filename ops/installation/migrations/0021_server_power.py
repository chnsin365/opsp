# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-13 15:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('installation', '0020_auto_20170709_1803'),
    ]

    operations = [
        migrations.AddField(
            model_name='server',
            name='power',
            field=models.BooleanField(default=True),
        ),
    ]