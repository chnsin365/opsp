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
# Create your views here.

def system(request):
	return render(request,'opsdb/system.html')

def system_iframe(request):
	systems = System.objects.all()
	return render(request,'opsdb/system_iframe.html',locals())

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
	