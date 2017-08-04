# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-04 07:48
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('opsdb', '0009_auto_20170804_1456'),
        ('auth', '0008_alter_user_username_max_length'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0010_auto_20170803_1124'),
    ]

    operations = [
        migrations.CreateModel(
            name='Rule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.TextField(blank=True, max_length=100)),
                ('applications', models.ManyToManyField(to='opsdb.Application')),
                ('businesses', models.ManyToManyField(to='opsdb.Business')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('group', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='group', to='auth.Group')),
                ('hostgroups', models.ManyToManyField(to='opsdb.HostGroup')),
            ],
            options={
                'db_table': 'rule',
            },
        ),
    ]
