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
from . import views

urlpatterns = [
    url(r'^post_server_info/',views.post_server_info,name='post_server_info'),
    url(r'^servers/',views.servers,name='servers'),
    url(r'^server/(\w+)/$',views.server_detail,name='server_detail'),
    url(r'^server/delete/(\w+)/$',views.server_delete,name='server_delete'),
    url(r'^server/edit/(\w+)/$',views.server_edit,name='server_edit'),
    url(r'^server/raid/(\w+)/(\w+)/$',views.server_raid,name='server_raid'),
    url(r'^select_cab/',views.select_cab,name='select_cab'),
    url(r'^server/status/(\w+)/$',views.server_change_status,name='server_change_status'),
    url(r'^server/ipmi/(\w+)/(\w+)/$',views.server_ipmi,name='server_ipmi'),
    url(r'^server/ipmi/(\w+)/$',views.update_ipmi,name='update_ipmi'),
    url(r'^server/install/(\w+)/$',views.install,name='install'),
    url(r'^server/add_system/(\w+)/$',views.add_system,name='add_system'),
    url(r'^server/system/view/(\w+)/$',views.view_system,name='view_system'),
    url(r'^server/system/delete/(\w+)/(\w+)/$',views.delete_system,name='delete_system'),
]