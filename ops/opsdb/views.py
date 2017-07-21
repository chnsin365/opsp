# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render,redirect
from django.shortcuts import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from .models import *
from ops.sshapi import remote_cmd,put_file
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import json
from json2html import *
from .saltapi import SaltAPI
import os

from pymongo import MongoClient
salt_mongo = get_object_or_404(ServiceHost,service='salt_mongo')
client = MongoClient(salt_mongo.ip,int(salt_mongo.port))
db_salt = client.salt 
# Create your views here.

def systems(request):
	return render(request,'opsdb/systems.html')

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

def salt_run(request):
	salt_funs = SaltFun.objects.all()
	if request.method == 'GET':
		pass
	else:
		salt_master = get_object_or_404(ServiceHost,service='salt_api')
		salt = SaltAPI(salt_master.ip,salt_master.user,salt_master.password,port=salt_master.port)
		token = salt.login()
		if token:
			fun = request.POST.get('fun','')
			arg_list = request.POST.get('arg_list','') if request.POST.get('arg_list','') else []
			target = request.POST.get('target','').split(',')
			result = salt.run(fun=fun,target=target,arg_list=arg_list)
			# result = json.dumps(ret,indent=4, sort_keys=False)
		else:
			result = '无法执行.'
	return render(request,'opsdb/salt_run.html',locals())

def salt_state(request):
	if request.method == 'GET':
		states = SaltState.objects.all()
	else:
		salt_master = get_object_or_404(ServiceHost,service='salt_api')
		salt = SaltAPI(salt_master.ip,salt_master.user,salt_master.password,port=salt_master.port)
		token = salt.login()
		if token:
			arg_list = request.POST.get('arg_list','')
			target = request.POST.get('target','').split(',')
			result = salt.run(fun='state.sls',target=target,arg_list=arg_list)
		else:
			result = '无法执行.'
	return render(request,'opsdb/salt_state.html',locals())


def state_manage(request):
	state_list = SaltState.objects.all()
	page_number =  request.GET.get('page_number')
	if page_number:
	    page_number = int(page_number)
	else:
	    page_number =  10
	paginator = Paginator(state_list, page_number)
	page = request.GET.get('page')
	try:
	    states = paginator.page(page)
	except PageNotAnInteger:
	    # If page is not an integer, deliver first page.
	    states = paginator.page(1)
	except EmptyPage:
	    # If page is out of range (e.g. 9999), deliver last page of results.
	    states = paginator.page(paginator.num_pages)
	return render(request,'opsdb/state_manage.html',locals())

def state_upload(request):
	if request.method == 'GET':
		# pass
		return render(request,'opsdb/upload_state.html')
	else:
		myFile = request.FILES.get("myfile", None)
        if not myFile:  
            messages.error(request, 'No files for upload!')
            return render(request,'opsdb/upload_state.html')
        else:
        	if not 'tar' in myFile.name:
        		messages.error(request, 'Must be archived a tar package!')
        		return render(request,'opsdb/upload_state.html')
        	else:	
				destination = open(os.path.join("/tmp",myFile.name),'wb+') 
				for chunk in myFile.chunks():
					destination.write(chunk)  
				destination.close()
				salt_master = get_object_or_404(ServiceHost,service='salt_master')
				try:
					localpath = "/tmp/%s"%(myFile.name)  
					# remotepath = "/srv/salt/%s"%(myFile.name)
					remotepath = "/srv/salt"
					remotefile = os.path.join(remotepath,myFile.name)
					ret1 = put_file(salt_master.ip,salt_master.user,salt_master.password,\
						localpath,remotefile,salt_master.port)
					if ret1['status']:
						cmd = "tar xvf %s -C %s;rm -f %s"%(remotefile,remotepath,remotefile)
						ret2 = remote_cmd(cmd,salt_master.ip,salt_master.port,salt_master.user,salt_master.password)
						if ret2['status'] and not ret2['err']:
							SaltState.objects.update_or_create(name=myFile.name.split('.')[0],defaults={'path':remotepath,'owner':request.user.username})
							messages.success(request, 'Upload over!')
						else:
							messages.error(request, ret2['result'])
					else:
						messages.error(request, ret1['err'])
				except Exception as e:
					messages.error(request, str(e)) 
				return render(request,'opsdb/upload_state.html')
	
@csrf_exempt
def state_delete(request):
	ids = request.POST.getlist('ids[]','')
	ret_data = {}
	salt_master = get_object_or_404(ServiceHost,service='salt_master')
	for state_id in ids:
		try:
			state = get_object_or_404(SaltState,pk=state_id)
			cmd = "rm -rf %s"%(os.path.join(state.path,state.name))
			ret = remote_cmd(cmd,salt_master.ip,salt_master.port,salt_master.user,salt_master.password)
			if ret['status'] and not ret['err']:
				state.delete()
			else:
				ret_data[state.name] = ret['result']
		except Exception as e:
			ret_data[state.name] = str(e)
	return HttpResponse(json.dumps(ret_data))




