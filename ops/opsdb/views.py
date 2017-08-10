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
import time
from django.contrib.auth.decorators import login_required
from users.custom_decorators import role_required
from django.contrib.auth.models import User,Group
from installation.models import Environment

# connect mongodb
try:
	from pymongo import MongoClient
	salt_mongo = get_object_or_404(ServiceHost,service='salt_mongo')
	client = MongoClient(salt_mongo.ip,int(salt_mongo.port))
	mongo_salt = client.salt 
except Exception as e:
	# raise e
	pass

def systems(request):
	system_list = System.objects.select_related().filter(is_delete=False)
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
	return render(request,'opsdb/host/systems.html',locals())


def system(request,id):
	system = mongo_salt.salt_grains.find_one({'id':id})
	if system:
		system_detail = json2html.convert(json = system['return'])
	else:
		system_detail = '抱歉,未查询到当前主机信息'
	return HttpResponse(system_detail)



@login_required
@role_required('hostadmin','admin')
@csrf_exempt
def add_system(request):
	if request.method == "GET":
		return render(request,'opsdb/host/add_system.html')
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
		return render(request,'opsdb/host/add_system.html',locals())

@login_required
@role_required('hostadmin','admin')
@csrf_exempt
def edit_system(request,id):
	hostgroups = HostGroup.objects.all()
	apps = Application.objects.all()
	system = get_object_or_404(System,pk=id)
	if request.method == "GET":
		return render(request,'opsdb/host/edit_system.html',locals())
	else:
		hostgroup_list = request.POST.getlist('hostgroups','')
		app_list = request.POST.getlist('apps','')
		try:
			system.hostgroups = hostgroup_list
			system.applications = app_list
			result = {'status':True,'msg':'变更成功'}
		except Exception as e:
			result = {'status':False,'msg':str(e)}
		return render(request,'opsdb/host/edit_system.html',locals())

@login_required
@role_required('hostadmin','admin')
@csrf_exempt
def delete_system(request):
	target = request.POST.get('ids[]','')
	salt_master = get_object_or_404(ServiceHost,service='salt_api')
	salt = SaltAPI(salt_master.ip,salt_master.user,salt_master.password,port=salt_master.port)
	ret = {}
	for tgt in target:
		try:
			salt.key(client='wheel',fun='key.delete',match=tgt)
			System.objects.filter(pk=tgt).update(is_delete=True)
		except Exception as e:
			ret[tgt] = str(e)
	return HttpResponse(ret)

@login_required
@role_required('hostadmin','admin')
def grouplist(request):
	group_list = HostGroup.objects.all()
	page_number =  request.GET.get('page_number')
	if page_number:
	    page_number = int(page_number)
	else:
	    page_number =  10
	paginator = Paginator(group_list, page_number)
	page = request.GET.get('page')
	try:
	    hostgroups = paginator.page(page)
	except PageNotAnInteger:
	    # If page is not an integer, deliver first page.
	    hostgroups = paginator.page(1)
	except EmptyPage:
	    # If page is out of range (e.g. 9999), deliver last page of results.
	    hostgroups = paginator.page(paginator.num_pages)
	return render(request,'opsdb/host/grouplist.html',locals())

@login_required
@role_required('hostadmin','admin')
def add_hostgroup(request):
	systems = System.objects.select_related().filter(is_delete=False)
	groups = Group.objects.all()
	if request.method == "GET":
		return render(request, 'opsdb/host/add_hostgroup.html',locals())
	else:
		name = request.POST.get('name','')
		systems_list = request.POST.getlist('systems','')
		groups_list = request.POST.getlist('groups','')
		comment = request.POST.get('comment','')
		try:
			hostgroup,created = HostGroup.objects.get_or_create(name=name)
			if created:
				hostgroup.groups = groups_list
				hostgroup.system_set = systems_list
				if comment:
					hostgroup.comment = comment
					hostgroup.save()
			result = {'status':True,'msg':'添加成功'}
		except Exception as e:
			result = {'status':False,'msg':str(e)}
		return render(request, 'opsdb/host/add_hostgroup.html',locals())

@login_required
@role_required('hostadmin','admin')
def edit_hostgroup(request,id):
	systems = System.objects.select_related().filter(is_delete=False)
	groups = Group.objects.all()
	hostgroup = HostGroup.objects.get(pk=id)
	if request.method == "GET":
		return render(request, 'opsdb/host/edit_hostgroup.html',locals())
	else:
		name = request.POST.get('name','')
		systems_list = request.POST.getlist('systems','')
		groups_list = request.POST.getlist('groups','')
		comment = request.POST.get('comment','')
		try:
			if name != hostgroup.name:
				hostgroup.name = name
			if comment != hostgroup.comment:
				hostgroup.comment = comment
			hostgroup.system_set = systems_list
			hostgroup.groups = groups_list
			hostgroup.save()
			result = {'status':True,'msg':'更新成功'}
		except Exception as e:
			result = {'status':False,'msg':str(e)}
		hostgroup = HostGroup.objects.get(pk=id)
		return render(request, 'opsdb/host/edit_hostgroup.html',locals())

@login_required
@role_required('hostadmin','admin')
@csrf_exempt
def delete_hostgroup(request):
	ids = request.POST.getlist('ids[]','')
	result = {}
	for group_id in ids:
		try:
			HostGroup.objects.filter(pk=group_id).delete()
		except Exception as e:
			result[group_id] = str(e)
	return HttpResponse(json.dumps(result))


@login_required
@role_required('salt','admin')
def salt_run(request):
	salt_funs = SaltFun.objects.all()
	if request.method == 'GET':
		pass
	else:
		user = request.user.username
		if request.META.has_key('HTTP_X_FORWARDED_FOR'):
			client =  request.META['HTTP_X_FORWARDED_FOR']  
		else:
			client = request.META['REMOTE_ADDR']
		salt_master = get_object_or_404(ServiceHost,service='salt_api')
		salt = SaltAPI(salt_master.ip,salt_master.user,salt_master.password,port=salt_master.port)
		try:
			fun = request.POST.get('fun','')
			arg_list = request.POST.get('arg_list','') if request.POST.get('arg_list','') else []
			target = request.POST.get('target','').split(',')
			result = salt.run(fun=fun,target=target,arg_list=arg_list)
			job = {'user':user,'time':time.strftime("%Y-%m-%d %X", time.localtime()),'client':client,\
			'target':target,'fun':fun,'arg':arg_list,\
			'status':'','progress':'Finish','result':result,'cjid':str(int(round(time.time() * 1000)))}
			mongo_salt.salt_joblist.insert_one(job)
		except Exception as e:
			result = ''
			error = str(e)
	return render(request,'opsdb/salt/salt_run.html',locals())

@login_required
@role_required('salt','admin')
def salt_custom_run(request,arg_list):
	user = request.user.username
	if request.META.has_key('HTTP_X_FORWARDED_FOR'):
		client =  request.META['HTTP_X_FORWARDED_FOR']  
	else:
		client = request.META['REMOTE_ADDR']
	salt_master = get_object_or_404(ServiceHost,service='salt_api')
	salt = SaltAPI(salt_master.ip,salt_master.user,salt_master.password,port=salt_master.port)
	try:
		result = salt.run(fun='cmd.run',target=salt_master.hostname,arg_list=arg_list)
		job = {'user':user,'time':time.strftime("%Y-%m-%d %X", time.localtime()),'client':client,\
		'target':target,'fun':fun,'arg':arg_list,\
		'status':'','progress':'Finish','result':result,'cjid':str(int(round(time.time() * 1000)))}
		mongo_salt.salt_joblist.insert_one(job)
	except Exception as e:
		result = ''
		error = str(e)	
	return render(request,'opsdb/salt/salt_run.html',locals())

@login_required
@role_required('salt','admin')
def salt_state(request):
	states = SaltState.objects.all()
	if request.method == 'GET':
		pass
	else:
		user = request.user.username
		if request.META.has_key('HTTP_X_FORWARDED_FOR'):
			client =  request.META['HTTP_X_FORWARDED_FOR']  
		else:
			client = request.META['REMOTE_ADDR']
		salt_master = get_object_or_404(ServiceHost,service='salt_api')
		salt = SaltAPI(salt_master.ip,salt_master.user,salt_master.password,port=salt_master.port)
		try:
			arg_list = request.POST.get('arg_list','')
			target = request.POST.get('target','').split(',')
			result = {}
			err = []
			for tgt in target:
				metadata = ''.join(map(lambda xx:(hex(ord(xx))[2:]),os.urandom(16)))
				cmd = 'salt %s state.sls %s --metadata=%s'%(tgt,arg_list,metadata)
				jid = salt.run_async(fun='cmd.run',target=salt_master.hostname,arg_list=cmd)
				result[tgt] = jid['jid']
				job = {'user':user,'time':time.strftime("%Y-%m-%d %X", time.localtime()),'client':client,\
				'target':[tgt],'fun':'state.sls','arg':arg_list,'jid':jid['jid'],\
				'status':'','progress':'Executing','metadata':metadata}
				mongo_salt.salt_joblist.insert_one(job)
		except Exception as e:
			err.append(str(e))
	return render(request,'opsdb/salt/salt_state.html',locals())

@login_required
@role_required('salt','admin')
def saltjoblist(request):
	sjobs = mongo_salt.salt_joblist.find().sort([('_id',-1)])
	job_list = [job for job in sjobs]
	page_number =  request.GET.get('page_number')
	if page_number:
	    page_number = int(page_number)
	else:
	    page_number =  10
	paginator = Paginator(job_list, page_number)
	page = request.GET.get('page')
	try:
	    jobs = paginator.page(page)
	except PageNotAnInteger:
	    # If page is not an integer, deliver first page.
	    jobs = paginator.page(1)
	except EmptyPage:
	    # If page is out of range (e.g. 9999), deliver last page of results.
	    jobs = paginator.page(paginator.num_pages)
	return render(request,'opsdb/salt/salt_jobs.html',locals())

def job_cjid(request,cjid):
	sjob = mongo_salt.salt_joblist.find_one({'cjid':cjid})
	return render(request,'opsdb/salt/salt_job_result.html',locals())

def job_jid(request,jid):
	sjob = mongo_salt.salt_job_ret.find_one({'jid':jid})
	return render(request,'opsdb/salt/salt_job_result.html',locals())

@login_required
@role_required('salt','admin')
def kill_job(request,jid):
	sjob = mongo_salt.salt_joblist.find_one({'jid':jid})
	if sjob.has_key('state_id') and sjob['progress'] == 'Executing':
		salt_master = get_object_or_404(ServiceHost,service='salt_api')
		salt = SaltAPI(salt_master.ip,salt_master.user,salt_master.password,port=salt_master.port)
		cmd = 'salt %s saltutil.kill_job %s'%(sjob['target'][0],sjob['state_id'])
		result = salt.run(fun='cmd.run',target=salt_master.hostname,arg_list=cmd)
		mongo_salt.salt_joblist.update_one({'jid':jid},{'$set':{'status':'Faield','killed':'Killed'}})
		result = 'Successfully'
	else:
		result = '无法kill该job'
	return HttpResponse(result)

@login_required
@role_required('salt','admin')
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
	return render(request,'opsdb/salt/state_manage.html',locals())

@login_required
@role_required('salt','admin')
def state_upload(request):
	if request.method == 'GET':
		# pass
		return render(request,'opsdb/salt/upload_state.html')
	else:
		myFile = request.FILES.get("myfile", None)
        if not myFile:  
            messages.error(request, 'No files for upload!')
            return render(request,'opsdb/salt/upload_state.html')
        else:
        	if not 'tar' in myFile.name:
        		messages.error(request, 'Must be archived a tar package!')
        		return render(request,'opsdb/salt/upload_state.html')
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
				return render(request,'opsdb/salt/upload_state.html')

@login_required
@role_required('salt','admin')	
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

@login_required
@role_required('salt','admin')
def minion_key(request,act):
	# minion_keys = mongo_salt.salt_key.find({'act':act})
	# key_list = [{'id': key['id'],'act':key['act'],'stamp':key['_stamp']} for key in minion_keys]
	salt_master = get_object_or_404(ServiceHost,service='salt_api')
	try:
		salt = SaltAPI(salt_master.ip,salt_master.user,salt_master.password,port=salt_master.port)
		ret = salt.key(client='wheel',fun='key.list_all',match=[])
		if act == 'pend':
			key_list = ret['data']['return']['minions_pre']
		else:
			key_list = ret['data']['return']['minions']
	except Exception as e:
		raise e
	page_number =  request.GET.get('page_number')
	if page_number:
	    page_number = int(page_number)
	else:
	    page_number =  10
	print key_list
	paginator = Paginator(key_list, page_number)
	page = request.GET.get('page')
	try:
	    keys = paginator.page(page)
	except PageNotAnInteger:
	    keys = paginator.page(1)
	except EmptyPage:
	    keys = paginator.page(paginator.num_pages)
	if act == 'pend':
		return render(request,'opsdb/salt/minion_key.html',locals())
	else:
		return render(request,'opsdb/salt/accept_key.html',locals())

@login_required
@role_required('salt','admin')
@csrf_exempt
def act_key(request):
	salt_master = get_object_or_404(ServiceHost,service='salt_api')
	salt = SaltAPI(salt_master.ip,salt_master.user,salt_master.password,port=salt_master.port)
	result = {'status':True,'comment':''}
	act = request.POST.get('act','')
	ids = request.POST.getlist('ids[]','')
	try:
		if act == 'accept':
			ret = salt.key(client='wheel',fun='key.accept',match=ids)
		else:
			ret = salt.key(client='wheel',fun='key.delete',match=ids)
		result['comment'] = ret['data']['return']['minions']
	except Exception as e:
		result = {'status':False,'comment':str(e)}
	return HttpResponse(json.dumps(result))

@login_required
@role_required('admin')
def envlist(request):
	env_obj = Environment.objects.all()
	env_list = []
	for env in env_obj:
		data = {}
		data['env_id'] = env.id
		data['env_name'] = env.name
		data['comment'] = env.comment
		data['busi_cnt'] = env.business_set.count()
		data['app_cnt'] = 0
		for business in env.business_set.all():
			data['app_cnt'] += business.application_set.count()
			data['host_cnt'] = 0
			for app in business.application_set.all():
				data['host_cnt'] += app.system_set.count()
		env_list.append(data)
	page_number =  request.GET.get('page_number')
	if page_number:
	    page_number = int(page_number)
	else:
	    page_number =  10
	paginator = Paginator(env_list, page_number)
	page = request.GET.get('page')
	try:
	    envs = paginator.page(page)
	except PageNotAnInteger:
	    # If page is not an integer, deliver first page.
	    envs = paginator.page(1)
	except EmptyPage:
	    # If page is out of range (e.g. 9999), deliver last page of results.
	    envs = paginator.page(paginator.num_pages)
	return render(request,'opsdb/env/envlist.html',locals())

@login_required
@role_required('admin')
def add_env(request):
	businesses = Business.objects.select_related().all()
	if request.method == "GET":
		return render(request, 'opsdb/env/add_env.html',locals())
	else:
		name = request.POST.get('name','')
		businesses_list = request.POST.getlist('businesses','')
		comment = request.POST.get('comment','')
		try:
			env = Environment.objects.create(name=name)
			if env:
				env.business_set = businesses_list
				if comment:
					env.comment = comment
					env.save()
			result = {'status':True,'msg':'添加成功'}
		except Exception as e:
			result = {'status':False,'msg':str(e)}
		return render(request, 'opsdb/env/add_env.html',locals())


@login_required
@role_required('admin')
def edit_env(request,id):
	businesses = Business.objects.select_related().all()
	env = Environment.objects.get(pk=id)
	if request.method == "GET":
		return render(request, 'opsdb/env/edit_env.html',locals())
	else:
		name = request.POST.get('name','')
		businesses_list = request.POST.getlist('businesses','')
		comment = request.POST.get('comment','')
		try:
			if env:
				if name != env.name:
					env.name = name
				if comment != env.comment:
					env.comment = comment
				env.save()
				if businesses_list:
					env.business_set.set([Business.objects.get(pk=busi_id) for busi_id in businesses_list])
			result = {'status':True,'msg':'更新成功'}
		except Exception as e:
			result = {'status':False,'msg':str(e)}
		env = Environment.objects.get(pk=id)
		return render(request, 'opsdb/env/edit_env.html',locals())

@login_required
@role_required('admin')
@csrf_exempt
def delete_env(request):
	ids = request.POST.getlist('ids[]','')
	result = {}
	for env_id in ids:
		try:
			env = Environment.objects.get(pk=env_id)
			env.delete()
		except Exception as e:
			result[env.name] = str(e)
	return HttpResponse(json.dumps(result))

@login_required
@role_required('busiadmin','admin')
def busilist(request):
	busi_obj = Business.objects.all()
	busi_list = []
	for busi in busi_obj:
		data = {}
		data['busi_id'] = busi.id
		data['busi_env'] = busi.environment.name
		data['busi_name'] = busi.name
		data['comment'] = busi.comment
		data['app_cnt'] = busi.application_set.count()
		data['host_cnt'] = 0
		for app in busi.application_set.all():
			data['host_cnt'] += app.system_set.count()
		busi_list.append(data)
	page_number =  request.GET.get('page_number')
	if page_number:
	    page_number = int(page_number)
	else:
	    page_number =  10
	paginator = Paginator(busi_list, page_number)
	page = request.GET.get('page')
	try:
	    businesses = paginator.page(page)
	except PageNotAnInteger:
	    # If page is not an integer, deliver first page.
	    businesses = paginator.page(1)
	except EmptyPage:
	    # If page is out of range (e.g. 9999), deliver last page of results.
	    businesses = paginator.page(paginator.num_pages)
	return render(request,'opsdb/business/busilist.html',locals())

@login_required
@role_required('busiadmin','admin')
def add_busi(request):
	apps = Application.objects.select_related().all()
	envs = Environment.objects.all()
	usergroups = Group.objects.all()
	if request.method == "GET":
		return render(request, 'opsdb/business/add_busi.html',locals())
	else:
		name = request.POST.get('name','')
		env_id = request.POST.get('env','')
		group_list = request.POST.getlist('usergroups','')
		app_list = request.POST.getlist('apps','')
		comment = request.POST.get('comment','')
		try:
			busi = Business.objects.create(name=name,environment_id=env_id)
			if busi:
				busi.applications = app_list
				busi.groups = group_list
				if comment:
					busi.comment = comment
					busi.save()
			result = {'status':True,'msg':'添加成功'}
		except Exception as e:
			result = {'status':False,'msg':str(e)}
		return render(request, 'opsdb/business/add_busi.html',locals())

@login_required
@role_required('busiadmin','admin')
def edit_busi(request,id):
	apps = Application.objects.select_related().all()
	envs = Environment.objects.all()
	usergroups = Group.objects.all()
	busi = Business.objects.get(pk=id)
	if request.method == "GET":
		return render(request, 'opsdb/business/edit_busi.html',locals())
	else:
		name = request.POST.get('name','')
		env_id = request.POST.get('env','')
		group_list = request.POST.getlist('usergroups','')
		app_list = request.POST.getlist('apps','')
		comment = request.POST.get('comment','')
		try:
			if busi:
				if name != busi.name:
					busi.name = name
				if comment != busi.comment:
					busi.comment = comment
				if busi.environment.id != env_id:
					busi.environment.id = env_id
				busi.groups = group_list
				busi.applications = app_list
				busi.save()
			result = {'status':True,'msg':'添加成功'}
		except Exception as e:
			result = {'status':False,'msg':str(e)}
		return render(request, 'opsdb/business/edit_busi.html',locals())

@login_required
@role_required('busiadmin','admin')
@csrf_exempt
def delete_busi(request):
	ids = request.POST.getlist('ids[]','')
	result = {}
	for busi_id in ids:
		try:
			busi = Business.objects.get(pk=busi_id)
			busi.delete()
		except Exception as e:
			result[busi.name] = str(e)
	return HttpResponse(json.dumps(result))

@login_required
@role_required('appadmin','admin')
def applist(request):
	app_objs = Application.objects.all()
	app_list = []
	for app in app_objs:
		data = {}
		data['app_id'] = app.id
		data['app_name'] = app.name
		data['app_busi'] = app.business.name if app.business else ''
		data['app_env'] = app.business.environment.name if app.business else ''
		data['comment'] = app.comment
		data['host_cnt'] = app.system_set.count()
		app_list.append(data)
	page_number =  request.GET.get('page_number')
	if page_number:
	    page_number = int(page_number)
	else:
	    page_number =  10
	paginator = Paginator(app_list, page_number)
	page = request.GET.get('page')
	try:
	    apps = paginator.page(page)
	except PageNotAnInteger:
	    # If page is not an integer, deliver first page.
	    apps = paginator.page(1)
	except EmptyPage:
	    # If page is out of range (e.g. 9999), deliver last page of results.
	    apps = paginator.page(paginator.num_pages)
	return render(request,'opsdb/app/applist.html',locals())

@login_required
@role_required('appadmin','admin')
def add_app(request):
	businesses = Business.objects.select_related().all()
	systems = System.objects.select_related().all()
	usergroups = Group.objects.all()
	if request.method == "GET":
		return render(request, 'opsdb/app/add_app.html',locals())
	else:
		name = request.POST.get('name','')
		usergroup_list = request.POST.getlist('usergroups','')
		business = request.POST.get('business','')
		system_list = request.POST.getlist('systems','')
		comment = request.POST.get('comment','')
		try:
			app = Application.objects.create(name=name,comment=comment)
			if app:
				if business:
					app.business = Business.objects.get(pk=business)
				app.system_set = system_list
				app.groups = usergroup_list
				app.save()
			result = {'status':True,'msg':'添加成功'}
		except Exception as e:
			result = {'status':False,'msg':str(e)}
		return render(request, 'opsdb/app/add_app.html',locals())

@login_required
@role_required('appadmin','admin')
def edit_app(request,id):
	businesses = Business.objects.select_related().all()
	systems = System.objects.select_related().all()
	usergroups = Group.objects.all()
	app = Application.objects.get(pk=id)
	if request.method == "GET":
		return render(request, 'opsdb/app/edit_app.html',locals())
	else:
		name = request.POST.get('name','')
		usergroup_list = request.POST.getlist('usergroups','')
		business = request.POST.get('business','')
		system_list = request.POST.getlist('systems','')
		comment = request.POST.get('comment','')
		try:
			if app:
				app.system_set = system_list
				app.groups = usergroup_list
				if business != app.business_id:
					app.business_id = business
				if name != app.name:
					app.name = name
				if comment != app.comment:
					app.comment = comment
				app.save()
			result = {'status':True,'msg':'更新成功'}
		except Exception as e:
			result = {'status':False,'msg':str(e)}
		return render(request, 'opsdb/app/edit_app.html',locals())

@login_required
@role_required('appadmin','admin')
@csrf_exempt
def delete_app(request):
	ids = request.POST.getlist('ids[]','')
	result = {}
	for app_id in ids:
		try:
			app = Application.objects.get(pk=app_id)
			app.delete()
		except Exception as e:
			result[app.name] = str(e)
	return HttpResponse(json.dumps(result))