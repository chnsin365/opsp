# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-02 11:02
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20170802_1828'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='roles',
        ),
        migrations.AddField(
            model_name='profile',
            name='roles',
            field=models.ForeignKey(default=3, on_delete=django.db.models.deletion.CASCADE, to='users.Role'),
            preserve_default=False,
        ),
    ]