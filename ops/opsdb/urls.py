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
from django.conf.urls import url,include
from django.contrib import admin
from django.views.decorators.csrf import csrf_exempt
from . import views

urlpatterns = [
	url(r'^systems/$',views.systems,name='systems'),
    url(r'^systems/show/(.+)/$',views.system,name='system'),
	url(r'^systems/add/$',views.add_system,name='add_system'),
    url(r'^systems/edit/(.+)/$',views.edit_system,name='edit_system'),
    url(r'^systems/delete/$',views.delete_system,name='delete_system'),
    url(r'^systems/remote_run/$',views.salt_run,name='salt_run'),
    url(r'^systems/state_deploy/$',views.salt_state,name='salt_state'),
    url(r'^systems/state_manage/$',views.state_manage,name='state_manage'),
    url(r'^systems/state_upload/$',views.state_upload,name='state_upload'),
    url(r'^systems/state_delete/$',views.state_delete,name='state_delete'),
    url(r'^systems/minion_key/(\w+)/$',views.minion_key,name='minion_key'),
    url(r'^systems/act_key/$',views.act_key,name='act_key'),
    url(r'^systems/saltjoblist/$',views.saltjoblist,name='saltjoblist'),
    url(r'^systems/job_cjid/(\d*)/$',views.job_cjid,name='job_cjid'),
    url(r'^systems/job_jid/(\d*)/$',views.job_jid,name='job_jid'),
    url(r'^systems/kill_job/(\d+)/$',views.kill_job,name='kill_job'),
    url(r'^systems/kill_job/(\d+)/$',views.kill_job,name='kill_job'),
    url(r'^hostgroup/grouplist/$',views.grouplist,name='grouplist'),
    url(r'^hostgroup/add/$',views.add_hostgroup,name='add_hostgroup'),
    url(r'^hostgroup/edit/(\d+)/$',views.edit_hostgroup,name='edit_hostgroup'),
    url(r'^hostgroup/delete/$',views.delete_hostgroup,name='delete_hostgroup'),
    url(r'^environment/envlist/$',views.envlist,name='envlist'),
    url(r'^environment/add_env/$',views.add_env,name='add_env'),
    url(r'^environment/edit_env/(\d+)/$',views.edit_env,name='edit_env'),
    url(r'^environment/delete/$',views.delete_env,name='delete_env'),
    url(r'^business/busilist/$',views.busilist,name='busilist'),
    url(r'^business/add_busi/$',views.add_busi,name='add_busi'),
    url(r'^business/edit_busi/(\d+)/$',views.edit_busi,name='edit_busi'),
    url(r'^business/delete/$',views.delete_busi,name='delete_busi'),
    url(r'^application/applist/$',views.applist,name='applist'),
    url(r'^application/add_app/$',views.add_app,name='add_app'),
    url(r'^application/edit_app/(\d+)/$',views.edit_app,name='edit_app'),
    url(r'^application/delete/$',views.delete_app,name='delete_app'),
]












