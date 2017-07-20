# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-20 07:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('opsdb', '0002_saltfun'),
    ]

    operations = [
        migrations.CreateModel(
            name='Salt',
            fields=[
                ('id', models.AutoField(db_column='salt_id', primary_key=True, serialize=False)),
                ('ip', models.GenericIPAddressField(blank=True, null=True, unique=True)),
                ('user', models.CharField(blank=True, max_length=50, null=True)),
                ('password', models.CharField(blank=True, max_length=50, null=True)),
            ],
            options={
                'db_table': 'salt',
            },
        ),
    ]
