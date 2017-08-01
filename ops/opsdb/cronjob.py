#!/bin/env python
#coding=utf8

'''
author: wei.yang@jinmuinfo.com
date: 2017.07.28

function:
cronjob for app opsdb

requirements:
1、pip install django-crontab
'''

from .saltapi import SaltAPI
from .models import System,ServiceHost
from django.shortcuts import get_object_or_404
import nmap
import os


def check_minion_and_power():
	'''
	monitoring host power status and salt-minion status
	'''
	try:
		salt_master = get_object_or_404(ServiceHost,service='salt_api')
		salt = SaltAPI(salt_master.ip,salt_master.user,salt_master.password,port=salt_master.port)
		ret = salt.minion_alive_check()
		if ret:
			for minion in ret:
				try:
					system = get_object_or_404(System,pk=minion)
					system.minion_status = False
					nm = nmap.PortScanner()
					nm.scan(system.ip,'22')
					if int(nm.scanstats()['downhosts']):
						system.power_status = False
					else:
						system.power_status = True
					system.save()
				except Exception as e:
					continue
	except Exception as e:
		print str(e)

def update_grains():
	'''
	update all hosts grains in a interval and need nmap and python-nmap
	'''
	try:
		salt_master = get_object_or_404(ServiceHost,service='salt_api')
		salt = SaltAPI(salt_master.ip,salt_master.user,salt_master.password,port=salt_master.port)
		salt.run(client='local_async', fun="grains.items", target="*", arg_list=['--batch=10%'],expr_form='glob')
	except Exception as e:
		pass


