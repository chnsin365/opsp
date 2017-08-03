# encoding:utf-8
from django.shortcuts import render,redirect
from django.contrib import auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .custom_decorators import role_required
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import User,Group
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
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
def new_user(request):
	if request.method == "GET":
		all_groups = Group.objects.all()
		return render(request, 'new_user.html',{'all_groups':all_groups})
	else:
		try:
			username = request.POST.get('username','')
			password = request.POST.get('password','')
			email = request.POST.get('email','')
			pn = request.POST.get('pn','')
			groups = request.POST.getlist('groups','')
			user = User.objects.create(username=username,email=email,first_name=pn)
			user.set_password(password)
			user.save()
			if groups:
				user.groups = groups
			messages.success(request, '%s has been created successfully!'%(user.username))
			Audit.objects.create(user=request.user,client=request.META['REMOTE_ADDR'],action='Create user %s'%((user.username)))
		except Exception as e:
			messages.error(request, e)
		return redirect('usermanage:users')

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
def new_group(request):
	if request.method == "GET":
		all_permissions = Permission.objects.filter(name__iregex=u'[\u4e00-\u9fa5]')
		return render(request, 'new_group.html',{'all_permissions':all_permissions})
	else:
		name = request.POST.get('name','')
		permissions = request.POST.getlist('permissions','')
		group = Group.objects.create(name=name)
		if permissions:
			group.permissions = permissions
		return redirect('usermanage:groups')

@login_required
@role_required('admin')
def edit_group(request,id):
	group = Group.objects.get(id=id)
	if request.method == "GET":
		all_permissions = Permission.objects.filter(name__iregex=u'[\u4e00-\u9fa5]')
		return render(request,'edit_group.html',{'all_permissions': all_permissions,'group':group})
	else:
		groups = request.POST.getlist('groups', '')
		group.permissions.clear()
		group.permissions = groups
		return redirect('usermanage:edit_group',id)

@login_required
@role_required('admin')
def delete_group(request,id):
	Group.objects.get(id=id).delete()
	return redirect('usermanage:groups')