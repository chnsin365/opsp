# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.

from django.contrib.auth.models import User,Group
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from opsdb.models import HostGroup,Application,Business

class Role(models.Model):
	name           = models.CharField(max_length=30, blank=True)
	comment        = models.TextField(max_length=100,blank=True)

	class Meta:
		db_table = 'role'

	def __str__(self):
		return self.name

class Profile(models.Model):
	user          = models.OneToOneField(User,related_name='profile', on_delete=models.CASCADE)
	roles         = models.ManyToManyField(Role)
	phone         = models.CharField(max_length=30, blank=True)
	wechat        = models.CharField(max_length=30, blank=True)
	date_expired  = models.DateTimeField(null=True)
	created_by    = models.ForeignKey(User,related_name='created_by',blank=True, null=True,on_delete=models.PROTECT)
	comment       = models.TextField(max_length=100,blank=True)

	class Meta:
		db_table = 'profile'

	def __str__(self):
		return self.user.username

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
	if created:
		Profile.objects.create(user=instance)
	instance.profile.save()

class Rule(models.Model):
	group         = models.OneToOneField(Group,related_name='rule', on_delete=models.CASCADE)
	hostgroups    = models.ManyToManyField(HostGroup)
	applications  = models.ManyToManyField(Application)
	businesses    = models.ManyToManyField(Business)
	created_by    = models.ForeignKey(User,blank=True, null=True,on_delete=models.PROTECT)
	comment       = models.TextField(max_length=100,blank=True)

	class Meta:
		db_table = 'rule'

	def __str__(self):
		return self.group.name

@receiver(post_save, sender=Group)
def create_or_update_group_rule(sender, instance, created, **kwargs):
	if created:
		Rule.objects.create(group=instance)
	instance.rule.save()		