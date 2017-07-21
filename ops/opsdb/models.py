# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from datetime import datetime
from installation.models import Environment


# Create your models here.

class HostGroup(models.Model):
	id                 = models.AutoField(primary_key=True,db_column="group_id") 
	name               = models.CharField(max_length=50,blank=True,null=True)

	class Meta:
		db_table = 'host_group'

	def __unicode__(self):
		return self.name

class Application(models.Model):
	id                 = models.AutoField(primary_key=True,db_column="app_id") 
	name               = models.CharField(max_length=50,blank=True,null=True)

	class Meta:
		db_table = 'application'

	def __unicode__(self):
		return self.name

class Business(models.Model):
	id                 = models.AutoField(primary_key=True,db_column="business_id") 
	name               = models.CharField(max_length=50,blank=True,null=True)
	application        = models.ManyToManyField(Application)

	class Meta:
		db_table = 'business'

	def __unicode__(self):
		return self.name

class System(models.Model):
    id                 = models.CharField(primary_key=True,max_length=100,db_column="system_id")
    ip                 = models.GenericIPAddressField(blank=True,null=True)
    os                 = models.CharField(max_length=100,blank=True,null=True)
    environment        = models.ForeignKey(Environment,blank=True, null=True,on_delete=models.PROTECT)
    hostgroup          = models.ForeignKey(HostGroup,blank=True, null=True,on_delete=models.PROTECT)
    application        = models.ManyToManyField(Application)
    business           = models.ManyToManyField(Business)
    create_time        = models.DateTimeField(auto_now_add=True)
    update_time        = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'system'

    def __unicode__(self):
        return self.id

class Salt(models.Model):
    id                 = models.AutoField(primary_key=True,db_column="salt_id")
    ip                 = models.GenericIPAddressField(blank=True,null=True,unique=True)
    port               = models.CharField(max_length=20,blank=True,null=True)
    user               = models.CharField(max_length=50,blank=True,null=True)
    password           = models.CharField(max_length=50,blank=True,null=True)

    class Meta:
        db_table = 'salt'
    
    def __unicode__(self):
        return self.ip

class SaltFun(models.Model):
    id                 = models.AutoField(primary_key=True,db_column="salt_fun_id")
    name               = models.CharField(max_length=100,blank=True,null=True)

    class Meta:
        db_table = 'salt_fun'

    def __unicode__(self):
        return self.name
