# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.

class System(models.Model):
    id                 = models.AutoField(primary_key=True,db_column="system_id")
    fqdn               = models.CharField(max_length=50,blank=True,null=True)
    create_time        = models.DateTimeField(auto_now_add=True)
    update_time        = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'system'

    def __unicode__(self):
        return self.fqdn

