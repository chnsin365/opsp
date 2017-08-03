"""ops URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'^$',views.users,name='users'),
	url(r'^userlist/$',views.userlist,name='userlist'),
    url(r'^add_user/$',views.add_user,name='add_user'),
	url(r'^grouplist/$',views.grouplist,name='grouplist'),
    url(r'^add_group/$',views.add_group,name='add_group'),
    url(r'^edit_group/(\d+)/$',views.edit_group,name='edit_group'),
    url(r'^delete_group/$',views.delete_group,name='delete_group'),
]