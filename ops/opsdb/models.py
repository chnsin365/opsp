# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from datetime import datetime
from installation.models import Environment
from django.contrib.auth.models import Group


# Create your models here.

class HostGroup(models.Model):
	id                 = models.AutoField(primary_key=True,db_column="group_id") 
	name               = models.CharField(max_length=50,blank=True,null=True)
	groups             = models.ManyToManyField(Group)
	comment            = models.TextField(max_length=200,blank=True)

	class Meta:
		db_table = 'hostgroup'

	def __unicode__(self):
		return self.name

class Business(models.Model):
	id                 = models.AutoField(primary_key=True,db_column="business_id") 
	name               = models.CharField(max_length=50,blank=True,null=True)
	environment        = models.ForeignKey(Environment,blank=True, null=True,on_delete=models.PROTECT)
	groups             = models.ManyToManyField(Group)
	comment            = models.TextField(max_length=200,blank=True)

	class Meta:
		db_table = 'business'

	def __unicode__(self):
		return self.name

class Application(models.Model):
	id                 = models.AutoField(primary_key=True,db_column="app_id") 
	name               = models.CharField(max_length=50,blank=True,null=True)
	business           = models.ForeignKey(Business,blank=True, null=True,on_delete=models.PROTECT)
	groups             = models.ManyToManyField(Group)
	comment            = models.TextField(max_length=200,blank=True)

	class Meta:
		db_table = 'application'

	def __unicode__(self):
		return self.name


class System(models.Model):
	id                 = models.CharField(primary_key=True,max_length=100,db_column="system_id")
	ip                 = models.GenericIPAddressField(blank=True,null=True)
	os                 = models.CharField(max_length=100,blank=True,null=True)
	num_cpus           = models.CharField(max_length=100,blank=True,null=True)
	mem_total          = models.CharField(max_length=100,blank=True,null=True)
	hostgroups         = models.ManyToManyField(HostGroup)
	applications       = models.ManyToManyField(Application)
	power_status       = models.BooleanField(default=True)
	minion_status      = models.BooleanField(default=True)
	is_delete          = models.BooleanField(default=False)
	comment            = models.TextField(max_length=200,blank=True)
	create_time        = models.DateTimeField(auto_now_add=True)
	update_time        = models.DateTimeField(auto_now=True)

	class Meta:
		db_table = 'system'

	def __unicode__(self):
		return self.id

class ServiceHost(models.Model):
	ip                 = models.GenericIPAddressField(blank=True,null=True)
	hostname           = models.CharField(max_length=100,blank=True,null=True)
	port               = models.CharField(max_length=20,blank=True,null=True)
	user               = models.CharField(max_length=50,blank=True,null=True)
	password           = models.CharField(max_length=50,blank=True,null=True)
	service            = models.CharField(max_length=50,blank=True,null=True)

	class Meta:
		db_table = 'service_host'
	
	def __unicode__(self):
		return self.ip

class SaltFun(models.Model):
	id                 = models.AutoField(primary_key=True,db_column="salt_fun_id")
	name               = models.CharField(max_length=100,blank=True,null=True)

	class Meta:
		db_table = 'salt_fun'

	def __unicode__(self):
		return self.name


class SaltState(models.Model):
	id                 = models.AutoField(primary_key=True,db_column="salt_state_id")
	name               = models.CharField(max_length=100,blank=True,null=True)
	path               = models.CharField(max_length=100,blank=True,null=True)
	owner              = models.CharField(max_length=100,blank=True,null=True)
	comment            = models.TextField(max_length=200,blank=True)
	create_time        = models.DateTimeField(auto_now_add=True)
	update_time        = models.DateTimeField(auto_now=True)   


	class Meta:
		db_table = 'salt_state'

	def __unicode__(self):
		return self.name