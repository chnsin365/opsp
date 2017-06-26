from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
# from usermanage.models import Audit

# Create your views here.

@login_required
def index(request):
    return render(request, 'index.html')

# Create your views here.

def login(request):
	if request.method == 'GET':
		if request.user.is_authenticated():
			return redirect('/')
		else:
			return render(request,'login.html')
	else:
		username = request.POST.get('username','')
		password = request.POST.get('password','')
		print username,password,'================'
		user = authenticate(username=username, password=password)
		if user is not None:
			if user.is_active:
				auth_login(request,user)
				return redirect('/')
			else:
				messages.error(request, 'The acount is not actived or not exsit.')
				return render(request,'login.html')
		else:
			msg = ''
			messages.error(request, 'The username or password is incorrect .')
			return render(request,'login.html')

@login_required
def logout(request):
	auth_logout(request)
	messages.info(request, 'Logout successfully !')
	return render(request,'login.html')