# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-20 02:05
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('installation', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.AutoField(db_column='app_id', primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, max_length=50, null=True)),
            ],
            options={
                'db_table': 'application',
            },
        ),
        migrations.CreateModel(
            name='Business',
            fields=[
                ('id', models.AutoField(db_column='business_id', primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, max_length=50, null=True)),
                ('application', models.ManyToManyField(to='opsdb.Application')),
            ],
            options={
                'db_table': 'business',
            },
        ),
        migrations.CreateModel(
            name='HostGroup',
            fields=[
                ('id', models.AutoField(db_column='group_id', primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, max_length=50, null=True)),
            ],
            options={
                'db_table': 'host_group',
            },
        ),
        migrations.CreateModel(
            name='System',
            fields=[
                ('id', models.CharField(db_column='system_id', max_length=100, primary_key=True, serialize=False)),
                ('ip', models.GenericIPAddressField(blank=True, null=True)),
                ('os', models.CharField(blank=True, max_length=100, null=True)),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now=True)),
                ('application', models.ManyToManyField(to='opsdb.Application')),
                ('business', models.ManyToManyField(to='opsdb.Business')),
                ('environment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='installation.Environment')),
                ('hostgroup', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='opsdb.HostGroup')),
            ],
            options={
                'db_table': 'system',
            },
        ),
    ]
