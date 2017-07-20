# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render,redirect
from django.shortcuts import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from .models import *
from ops.sshapi import remote_cmd
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import json
from json2html import *

from pymongo import MongoClient
client = MongoClient('192.168.3.167',27017)
db_salt = client.salt 
# Create your views here.

def systems(request):
	return render(request,'opsdb/systems.html')

# def system_iframe(request):
# 	systems  = db_salt.salt_grains.find()
# 	system_list = [system['return'] for system in systems if system.has_key('return')]
# 	page_number =  request.GET.get('page_number')
# 	if page_number:
# 	    page_number = int(page_number)
# 	else:
# 	    page_number =  10
# 	paginator = Paginator(system_list, page_number)
# 	page = request.GET.get('page')
# 	try:
# 	    systems = paginator.page(page)
# 	except PageNotAnInteger:
# 	    # If page is not an integer, deliver first page.
# 	    systems = paginator.page(1)
# 	except EmptyPage:
# 	    # If page is out of range (e.g. 9999), deliver last page of results.
# 	    systems = paginator.page(paginator.num_pages)
# 	return render(request,'opsdb/system_iframe.html',locals())
def system_iframe(request):
	system_list = System.objects.select_related().all()
	page_number =  request.GET.get('page_number')
	if page_number:
	    page_number = int(page_number)
	else:
	    page_number =  10
	paginator = Paginator(system_list, page_number)
	page = request.GET.get('page')
	try:
	    systems = paginator.page(page)
	except PageNotAnInteger:
	    # If page is not an integer, deliver first page.
	    systems = paginator.page(1)
	except EmptyPage:
	    # If page is out of range (e.g. 9999), deliver last page of results.
	    systems = paginator.page(paginator.num_pages)
	return render(request,'opsdb/system_iframe.html',locals())

def system(request,id):
	system = db_salt.salt_grains.find_one({'id':id})
	system_detail = json2html.convert(json = system['return'])
	# return render(request,'opsdreturn render(request,'opsdb/system_details.html',locals())b/system_details.html',locals())
	return HttpResponse(system_detail)


@csrf_exempt
def add_system(request):
	if request.method == "GET":
		return render(request,'opsdb/add_system.html')
	else:
		ip = request.POST.get('ip','')
		port = request.POST.get('port','')
		username = request.POST.get('username','')
		password = request.POST.get('password','')
		if ip and port and username and password:
			cmd = "curl -L http://192.168.3.166/cobbler/svc/install-minion.sh | sh"
			ret = remote_cmd(cmd,ip,port=int(port),user=username,passwd=password)
			if ret['status'] and not ret['err']:
				messages.success(request, '添加成功')
			else:
				messages.error(request, ret['result'])
		return render(request,'opsdb/add_system.html',locals())
	