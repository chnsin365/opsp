# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render,redirect
from django.shortcuts import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from .models import *
import json
from ops.sshapi import remote_cmd
import subprocess

# Create your views here.
@csrf_exempt
def post_server_info(request):
    server_info = json.loads(request.body)
    try:
        server,created = Server.objects.update_or_create(\
            pk = server_info['server_id'].split()[0],\
            defaults = {'sn':server_info['sn'],\
                        'cpu_model':server_info['cpu_model'],\
                        'cpu_sockets':server_info['cpu_sockets'],\
                        'cpu_cores':server_info['cpu_cores'],\
                        'cpu_threads':server_info['cpu_threads'],\
                        'mem_size':server_info['mem_size'],\
                        'mem_total_slots':server_info['mem_total_slots'],\
                        'mem_free_slots':server_info['mem_free_slots'],\
                        'raid_adapter':server_info['raid_adapter'],\
                        'raid_adapter_slot':server_info['raid_adapter_slot'],\
                        'ipmi_ip':server_info['ipmi_ip'],\
                        'pxe_mac':server_info['pxe_mac'],\
                        'pxe_ip':server_info['pxe_ip'],\
                        'vendor':server_info['vendor'],\
                        'model':server_info['model']})
        print server,created
        if created:
            tag = Tag.objects.get(tag_type=server_info['tag'])
            server.tag = tag
            if tag.tag_type == 'L':
                status = ServerStatus.objects.get(status_type='init')
            else:
                status = ServerStatus.objects.get(status_type='running')
            server.serverstatus = status
            server.save()
    except Exception as e:
        raise e
    return HttpResponse(created)

def servers(request):
    # status = get_object_or_404(ServerStatus)
    # servers = status.server_set.all()
    servers = Server.objects.select_related('serverstatus').filter(progress__lt=100)
    return render(request,'installation/servers.html',locals())

def server_detail(request,server_id):
    server = get_object_or_404(Server,pk=server_id)
    return render(request,'installation/server_detail.html',locals())

def server_delete(request,server_id):
    server = get_object_or_404(Server,pk=server_id).delete()
    return redirect('installation:servers')

def server_edit(request,server_id):
    server = get_object_or_404(Server,pk=server_id)
    if request.method == "GET":
        idcs = Idc.objects.all()
        cabinets = Cabinet.objects.all()
        contacters = Contacter.objects.all()
        environments = Environment.objects.all()
        location = range(50)
        return render(request,'installation/server_edit.html',locals())
    else:
        kwargs = {}
        for k,v in request.POST.dict().items():
            if k == 'csrfmiddlewaretoken':
                pass
            else:
                if v:
                    kwargs[k] = v
        print kwargs
        Server.objects.filter(pk=server_id).update(**kwargs)
        return redirect('installation:server_edit',server_id)

def server_change_status(request,server_id):
    server = get_object_or_404(Server,pk=server_id)
    if request.method == "GET":
        all_status = ServerStatus.objects.all()
        return render(request,'installation/change_status.html',locals())
    else:
        status_id = request.POST.get('status_id','')
        Server.objects.filter(pk=server_id).update(serverstatus_id=status_id)
        status = get_object_or_404(ServerStatus,pk=status_id)
        ret_data = '''%s 的状态已经更新。

当前状态：%s'''%(server.id,status.name)
        return render(request,'installation/tips.html',locals())

def select_cab(request):
    idc_id = request.GET.get('idc_id','')
    cabs = Cabinet.objects.filter(idc_id=idc_id)
    result = {}
    for cab in cabs:
        result[cab.id] = cab.name
    return HttpResponse("%s"%(json.dumps(result)))

def server_raid(request,server_id,fun):
    '''
    raid模块,包含以下方法：
    1、查看raid卡信息(包括控制器状态、Cache状态、电池状态) (raid_card)
    2、查看raid详细信息 （raid_detail）
    3、查看raid状态 (raid_status)
    4、查看物理硬盘状态 (raid_status)
    5、创建raid (create_raid)
    6、删除raid (delete_raid)
    '''
    server = get_object_or_404(Server,pk=server_id)
    addr = server.pxe_ip
    from .raid_api import RAIDAPI
    rd = RAIDAPI(server,addr,user='root',passwd='P@ssw0rd')
    if fun == 'raid_card':
        ret_data = rd.raid_card()
    elif fun == 'raid_detail':
        ret_data = rd.raid_detail()
    elif fun == 'raid_status':
        ret_data = rd.raid_status()
    elif fun == 'raid_disk':
        ret_data = rd.raid_disk()
    elif fun == 'create_raid':
        if request.method == 'GET':
            return render(request,'installation/create_raid.html',locals())
        else:
            drivers = ','.join(request.POST.getlist('drivers',''))
            raid_type = request.POST.get('raid_type','')
            ret_data = rd.create_raid(drivers,raid_type)
            if not ret_data:
                ret_data = 'Raid %s has been created on %s'%(raid_type,drivers)
            return render(request,'installation/tips.html',locals())
    elif fun == 'delete_raid':
        if request.method == 'GET':
            return render(request,'installation/delete_raid.html',locals())
        else:
            array = request.POST.get('array','')
            ret_data = rd.delete_raid(array)
            return render(request,'installation/tips.html',locals())
    return render(request,'installation/raid.html',locals())

def server_ipmi(request,server_id,fun):
    '''
    IPMI模块,包含以下方法：
    1、chassis_status
    2、chassis_on
    3、chassis_off
    4、chassis_reboot
    5、boot_to_pxe
    6、boot_to_disk
    '''
    server = get_object_or_404(Server,pk=server_id)
    ipmi_ip = server.ipmi_ip
    ipmi_user = server.ipmi_user
    ipmi_pass = server.ipmi_pass
    if (ipmi_ip and ipmi_user and ipmi_pass):
        try:
            from ops.ipmi_api import ipmitool
            ipmi = ipmitool(ipmi_ip,ipmi_pass,username=ipmi_user)
            ipmi.chassis_status()
            if fun == 'boot_to_disk':
                ipmi.boot_to_disk()
                ret_data = ipmi.output
            elif fun == 'chassis_on':
                if 'on' in ipmi.output:
                    ret_data = '已经在开机状态，已为您取消本次开机操作。'
                else:
                    ipmi.chassis_on()
                    ret_data = ipmi.output
            elif fun == 'chassis_off':
                if 'off' in ipmi.output:
                    ret_data = '已经在关机状态，已为您取消本次关机操作。'
                else:
                    ipmi.chassis_off()
                    ret_data = ipmi.output
                # return HttpResponse(ret_data)
            elif fun == 'chassis_reboot':
                if 'off' in ipmi.output:
                    ret_data = '当前在关机状态，无法完成重启操作。'
                else:
                    ipmi.chassis_reboot()
                    ret_data = ipmi.output
            elif fun == 'boot_to_pxe':
                ipmi.boot_to_pxe()
                ret_data = ipmi.output
            else:
                ret_data = ipmi.output
        except Exception as e:
            ret_data = str(e)
    else:
        ret_data = '''
无法完成操作，可能原因是ipmi的地址、账号或密码配置不正确。
当前的ipmi地址、账号和密码如下：
地址：%s
账号：%s
密码：%s
您可以尝试更新ipmi账号配置后继续该操作'''%(ipmi_ip,ipmi_user,ipmi_pass)
    return render(request,'installation/ipmi.html',locals())

def update_ipmi(request,server_id):
    server = get_object_or_404(Server,pk=server_id)
    if request.method == "GET":
        return render(request,'installation/update_ipmi.html',locals())
    else:
        kwargs = {}
        for k,v in request.POST.dict().items():
            if k == 'csrfmiddlewaretoken':
                pass
            else:
                if v:
                    kwargs[k] = v
        print kwargs
        Server.objects.filter(pk=server_id).update(**kwargs)
        ret_data = '''
ipmi的地址、账号或密码均已被更新。
当前的ipmi地址、账号和密码如下：
地址：%s
账号：%s
密码：%s'''%(kwargs['ipmi_ip'],kwargs['ipmi_user'],kwargs['ipmi_pass'])
        return render(request,'installation/tips.html',locals())

def install(request,server_id):
    server = get_object_or_404(Server,pk=server_id)
    return render(request,'installation/install.html',locals())

def add_system(request,server_id):
    server = get_object_or_404(Server,pk=server_id)
    if request.method == 'GET':
        return render(request,'installation/add_system.html',locals())
    else:
        return render(request,'installation/install.html',locals())


