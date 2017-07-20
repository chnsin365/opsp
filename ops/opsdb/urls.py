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
    url(r'^systems/module_delay/$',views.salt_state,name='salt_state'),
]