# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-04 08:22
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_rule'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rule',
            name='group',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='rule', to='auth.Group'),
        ),
    ]