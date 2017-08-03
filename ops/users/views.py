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
# Create your views here.

@login_required
@role_required('admin')
def users(request):
	return render(request,'users/users.html')

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
			password = request.POST.get('password','')
			roles = request.POST.getlist('roles','')
			groups = request.POST.getlist('groups','')
			is_active = bool(int(request.POST.get('is_active','')))
			date_expired = request.POST.get('date_expired','')
			email = request.POST.get('email','')
			phone = request.POST.get('phone','')
			wechat = request.POST.get('wechat','')
			comment = request.POST.get('comment','')
			user, created = User.objects.get_or_create(username=username,email=email,is_active=is_active)
			if created:
				user.set_password(password)
				user.profile.roles = roles
				user.profile.date_expired = date_expired
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
	if request.method == 'GET':
		all_groups = Group.objects.all()
		return render(request, 'edit_user.html', {'user': user,'all_groups':all_groups})
	else:
		username = request.POST.get('username', '')
		email = request.POST.get('email', '')
		pn = request.POST.get('pn', '')
		groups = request.POST.getlist('groups', '')
		user.username=username
		user.email=email
		user.first_name = pn
		user.save()
		user.groups.clear()
		user.groups = groups
		return redirect('usermanage:edit_user',id)

@login_required
@role_required('admin')
def delelte_user(request,id):
	User.objects.filter(id=id).delete()
	messages.success(request, 'Delete successfully!')
	Audit.objects.create(user=request.user,client=request.META['REMOTE_ADDR'],action='Delete user %s'%((user.username)))
	return redirect('usermanage:users')

@login_required
def changepwd(request):
	if request.method == 'GET':
		return render(request, 'changepwd.html')
	else:
		oldpassword = request.POST.get('oldpassword', '')
		user = auth.authenticate(username=request.user.username, password=oldpassword)
		if user:
			newpassword = request.POST.get('newpassword', '')
			newpassword1 = request.POST.get('newpassword1', '')
			if newpassword == newpassword1:
				user.set_password(newpassword)
				user.save()
				messages.success(request, 'Change password successfully!')
			else:
				messages.error(request, '两次输入密码不一致！')
		else:
			messages.error(request, '旧密码错误！')
		return redirect('usermanage:changepwd')

@login_required
@role_required('admin')
def resetpwd(request,id):
	if request.method == 'GET':
		return render(request, 'resetpwd.html',{'id':id})
	else:
		newpassword = request.POST.get('newpassword', '')
		newpassword1 = request.POST.get('newpassword1', '')
		if newpassword == newpassword1:
			user = User.objects.get(id=id)
			user.set_password(newpassword)
			user.save()
			messages.success(request, 'Change password successfully!')
		else:
			messages.error(request, '两次输入密码不一致！')
		return redirect('usermanage:resetpwd')

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
			group,created = Group.objects.get_or_create(name=name)
			if created and members:
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
	ids = request.POST.getlist('ids','')
	result = {}
	try:
		for group_id in ids:
			Group.objects.filter(pk=group_id).delete()
	except Exception as e:
		result[group_id] = str(e)
	return HttpResponse(json.dumps(result))