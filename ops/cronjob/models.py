# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.

class CronJob(models.Model):
	id                 = models.AutoField(primary_key=True,db_column="cronjob_id") 
	name               = models.CharField(max_length=50,blank=True,null=True)
	description        = models.CharField(max_length=50,blank=True,null=True)

	class Meta:
		db_table = 'cronjob'

	def __unicode__(self):
		return self.name
