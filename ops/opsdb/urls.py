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
	url(r'^system_iframe/',views.system_iframe,name='system_iframe'),
    url(r'^systems/show/(.+)/$',views.system,name='system'),
	url(r'^systems/add/$',views.add_system,name='add_system'),
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
]