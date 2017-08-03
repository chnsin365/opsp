# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

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