# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-07 04:39
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('installation', '0015_auto_20170707_1211'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='datastore',
            name='ip',
        ),
    ]
