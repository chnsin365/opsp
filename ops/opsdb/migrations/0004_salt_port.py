# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-20 09:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('opsdb', '0003_salt'),
    ]

    operations = [
        migrations.AddField(
            model_name='salt',
            name='port',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
