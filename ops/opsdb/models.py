# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from datetime import datetime

# Create your models here.

class System(models.Model):
    id                 = models.CharField(primary_key=True,max_length=100,db_column="system_id")
    create_time        = models.DateTimeField(auto_now_add=True)
    update_time        = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'system'

    def __unicode__(self):
        return self.fqdn

