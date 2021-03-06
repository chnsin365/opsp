# encoding:utf-8
from django.shortcuts import render,redirect
from django.shortcuts import HttpResponse
from django.contrib import auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .custom_decorators import role_required
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User,Group
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import json
from .models import *
from opsdb.models import HostGroup,Application,Business
# Create your views here.

@login_required
@role_required('admin')
def userlist(request):
	user_list = User.objects.all()
	page_number =  request.GET.get('page_number')
	if page_number:
		page_number = int(page_number)
	else:
		page_number =  10
	paginator = Paginator(user_list, page_number)
	page = request.GET.get('page')
	try:
		users = paginator.page(page)
	except PageNotAnInteger:
		# If page is not an integer, deliver first page.
		users = paginator.page(1)
	except EmptyPage:
		# If page is out of range (e.g. 9999), deliver last page of results.
		users = paginator.page(paginator.num_pages)
	return render(request,'users/userlist.html',locals())

@login_required
@role_required('admin')
@csrf_exempt
def add_user(request):
	roles = Role.objects.all()
	groups = Group.objects.all()
	if request.method == "GET":
		return render(request, 'users/add_user.html',locals())
	else:
		try:
			username = request.POST.get('username','')
			# password = request.POST.get('password','')
			roles = request.POST.getlist('roles','')
			groups = request.POST.getlist('groups','')
			is_active = bool(int(request.POST.get('is_active','')))
			# date_expired = request.POST.get('date_expired','')
			email = request.POST.get('email','')
			phone = request.POST.get('phone','')
			wechat = request.POST.get('wechat','')
			comment = request.POST.get('comment','')
			user = User.objects.create(username=username,email=email,is_active=is_active)
			if user:
				user.set_password("1qaz@WSX")
				user.profile.roles = roles
				# user.profile.date_expired = date_expired
				user.profile.created_by = request.user
				if phone:
					user.profile.phone = phone
				if wechat:
					user.profile.wechat = wechat
				if comment:
					user.profile.comment = comment
				user.groups = groups
				user.save()
			result = {'status':True,'msg':'添加成功'}
		except Exception as e:
			result = {'status':False,'msg':str(e)}
		return render(request, 'users/add_user.html',locals())

@login_required
@role_required('admin')
def edit_user(request,id):
	user = User.objects.get(id=id)
	roles = Role.objects.all()
	groups = Group.objects.all()
	if request.method == "GET":
		return render(request, 'users/edit_user.html',locals())
	else:
		try:
			username = request.POST.get('username','')
			new_roles = request.POST.getlist('roles','')
			new_groups = request.POST.getlist('groups','')
			# date_expired = request.POST.get('date_expired','')
			email = request.POST.get('email','')
			phone = request.POST.get('phone','')
			wechat = request.POST.get('wechat','')
			comment = request.POST.get('comment','')
			user.profile.roles = new_roles
			user.groups = new_groups
			# user.profile.date_expired = date_expired
			if username != user.username:
				user.username=username
			if email != user.email:
				user.email=email
			if phone != user.profile.phone:
				user.profile.phone = phone
			if wechat != user.profile.wechat:
				user.profile.wechat = wechat
			if comment != user.profile.comment:
				user.profile.comment = comment
			user.save()
			result = {'status':True,'msg':'更新成功'}
		except Exception as e:
			result = {'status':False,'msg':str(e)}
		user = User.objects.get(id=id)
		return render(request, 'users/edit_user.html',locals())

@login_required
@role_required('admin')
@csrf_exempt
def delete_user(request):
	ids = request.POST.getlist('ids[]','')
	result = {}
	for user_id in ids:
		try:
			user = User.objects.get(pk=user_id)
			user.delete()
		except Exception as e:
			result[user.username] = '错误原因:%s'%(str(e))
	return HttpResponse(json.dumps(result))


@login_required
@role_required('admin')
@csrf_exempt
def disable_user(request):
	ids = request.POST.getlist('ids','')
	result = {}
	for user_id in ids:
		try:
			user = User.objects.get(pk=user_id)
			user.is_active = not user.is_active
			user.save()
		except Exception as e:
			result[user.username] = '错误原因:%s'%(str(e))
	return HttpResponse(json.dumps(result))


@login_required
def profile(request,id):
	user = User.objects.get(id=id)
	if request.method == "GET":
		return render(request, 'users/profile.html',locals())
	else:
		try:
			username = request.POST.get('username','')
			email = request.POST.get('email','')
			phone = request.POST.get('phone','')
			wechat = request.POST.get('wechat','')
			comment = request.POST.get('comment','')
			if username != user.username:
				user.username=username
			if email != user.email:
				user.email=email
			if phone != user.profile.phone:
				user.profile.phone = phone
			if wechat != user.profile.wechat:
				user.profile.wechat = wechat
			if comment != user.profile.comment:
				user.profile.comment = comment
			user.save()
			result = {'status':True,'msg':'更新成功'}
		except Exception as e:
			result = {'status':False,'msg':str(e)}
		user = User.objects.get(id=id)
		return render(request, 'users/profile.html',locals())


@login_required
def changepwd(request):
	if request.method == 'GET':
		return render(request, 'users/changepwd.html')
	else:
		oldpassword = request.POST.get('oldpassword', '')
		user = auth.authenticate(username=request.user.username, password=oldpassword)
		if user:
			newpassword = request.POST.get('newpassword', '')
			newpassword1 = request.POST.get('newpassword1', '')
			if newpassword == newpassword1:
				user.set_password(newpassword)
				user.save()
				result = {'status':True,'msg':'密码修改成功'}
			else:
				result = {'status':False,'msg':'两次输入密码不同'}
		else:
			result = {'status':False,'msg':'旧密码错误！'}
		return render(request, 'users/changepwd.html',locals())

@login_required
@role_required('admin')
@csrf_exempt
def resetpwd(request):
	ids = request.POST.getlist('ids','')
	result = {}
	for user_id in ids:
		try:
			user = User.objects.get(pk=user_id)
			user.set_password('1qaz@WSX')
			user.save()
		except Exception as e:
			result[user.username] = '重置密码失败,原因:%s'%(str(e))
	return HttpResponse(json.dumps(result))

@login_required
@role_required('admin')
def grouplist(request):
	group_list = Group.objects.all()
	page_number =  request.GET.get('page_number')
	if page_number:
		page_number = int(page_number)
	else:
		page_number =  10
	paginator = Paginator(group_list, page_number)
	page = request.GET.get('page')
	try:
		groups = paginator.page(page)
	except PageNotAnInteger:
		# If page is not an integer, deliver first page.
		groups = paginator.page(1)
	except EmptyPage:
		# If page is out of range (e.g. 9999), deliver last page of results.
		groups = paginator.page(paginator.num_pages)
	return render(request, 'users/grouplist.html',locals())

@login_required
@role_required('admin')
@csrf_exempt
def add_group(request):
	users = User.objects.all()
	if request.method == "GET":
		return render(request, 'users/add_group.html',locals())
	else:
		name = request.POST.get('name','')
		members = request.POST.getlist('members','')
		try:
			group = Group.objects.create(name=name)
			if group and members:
				group.user_set = members
			result = {'status':True,'msg':'添加成功'}
		except Exception as e:
			result = {'status':False,'msg':str(e)}
		return render(request, 'users/add_group.html',locals())

@login_required
@role_required('admin')
@csrf_exempt
def edit_group(request,id):
	group = Group.objects.get(id=id)
	users = User.objects.all()
	if request.method == "GET":
		return render(request,'users/edit_group.html',locals())
	else:
		name = request.POST.get('name','')
		members = request.POST.getlist('members','')
		try:
			if group.name != name:
				group.update(name=name)
			group.user_set = members
			result = {'status':True,'msg':'更新成功'}
		except Exception as e:
			result = {'status':False,'msg':str(e)}
		return render(request, 'users/edit_group.html',locals())

@login_required
@role_required('admin')
@csrf_exempt
def delete_group(request):
	ids = request.POST.getlist('ids[]','')
	result = {}
	for group_id in ids:
		try:
			group = Group.objects.get(pk=group_id)
			group.delete()
		except Exception as e:
			result[group.name] = str(e)
	return HttpResponse(json.dumps(result))

@login_required
@role_required('admin')
def rulelist(request):
	rule_list = Rule.objects.all()
	page_number =  request.GET.get('page_number')
	if page_number:
		page_number = int(page_number)
	else:
		page_number =  10
	paginator = Paginator(rule_list, page_number)
	page = request.GET.get('page')
	try:
		rules = paginator.page(page)
	except PageNotAnInteger:
		# If page is not an integer, deliver first page.
		rules = paginator.page(1)
	except EmptyPage:
		# If page is out of range (e.g. 9999), deliver last page of results.
		rules = paginator.page(paginator.num_pages)	
	return render(request,'users/rulelist.html',locals())


@login_required
@role_required('admin')
@csrf_exempt
def edit_rule(request,id):
	hostgroups = HostGroup.objects.all()
	apps = Application.objects.all()
	businesses = Business.objects.all()
	rule = Rule.objects.get(pk=id)
	if request.method == "GET":
		return render(request, 'users/edit_rule.html',locals())
	else:
		try:
			hostgroups = request.POST.getlist('hostgroups','')
			apps = request.POST.getlist('apps','')
			businesses = request.POST.getlist('businesses','')
			comment = request.POST.get('comment','')
			rule.hostgroups = hostgroups
			rule.applications = apps
			rule.businesses = businesses
			rule.created_by = request.user
			rule.comment = comment
			rule.save()
			result = {'status':True,'msg':'添加成功'}
		except Exception as e:
			result = {'status':False,'msg':str(e)}
		rule = Rule.objects.get(pk=id)
		return render(request, 'users/edit_rule.html',locals())
