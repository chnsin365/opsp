# -*- coding: utf-8 -*-
from django.contrib.auth.models import User,Group
from installation.models import ServerStatus,Tag,Cobbler
from users.models import Role
import datetime

# create roles
roles = {'viewer':'访客','install':'装机操作','salt':'主机配置','hostadmin':'主机管理','appadmin':'应用管理','busiadmin':'业务管理','admin':'管理员'}
try:
    for name,comment in roles.items():
        Role.objects.get_or_create(name=name,defaults={'comment':comment})
        print '***********',name,comment,'***********'
except Exception as e:
    # raise e
    print e

# create admin user
try:
    user,created = User.objects.get_or_create(username='admin',defaults ={ 'is_superuser': True })
    if created:
        user.set_password('admin@123')
        role = Role.objects.get(name='admin')
        user.profile.roles.add(role)
        user.profile.created_by = user
        user.profile.date_expired = datetime.datetime(2100, 1, 2, 00, 00)
        user.save()
        group,created = Group.objects.get_or_create(name='admin')
        if created:
            user.groups.add(group)
    print '*************',user.username,'*************'
except Exception as e:
    print e
    raise e



# 创建数据来源<从LiveCD获取的信息会自动填入L，线上主机通过Agent抓取的为A>
tag = {'L':'livecd','A':'agent'}
try:
    for tag_type,description in tag.items():
        Tag.objects.get_or_create(tag_type=tag_type,defaults={'description':description})
        print '***********',tag_type,description,'***********'
except Exception as e:
    # raise e
    print e

    
# 创建物理服务器状态<初始化、安装系统、运行中、下线>
server_status = {'init':'初始化','install':'安装系统','running':'运行中','off_line':'下线'}
try:
    for status_type,status_name in server_status.items():
        ServerStatus.objects.get_or_create(status_type=status_type,defaults={'name':status_name})
        print '***********',status_type,status_name,'***********'
except Exception as e:
    # raise e
    print e

try:
    cobbler,created = Cobbler.objects.get_or_create(user='cobbler',defaults ={ 'ip': '0.0.0.0','password':'cobbler' })
    print '*************',cobbler.user,cobbler.ip,cobbler.password,'*************'
except Exception as e:
    print e
    raise e