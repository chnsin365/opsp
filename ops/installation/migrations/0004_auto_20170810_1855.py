# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-10 10:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('installation', '0003_environment_comment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='server',
            name='power',
            field=models.CharField(blank=True, default='on', max_length=10, null=True),
        ),
    ]
