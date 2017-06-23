# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render,redirect
from django.shortcuts import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from .models import *
import json
from ops.sshapi import remote_cmd

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
    servers = Server.objects.select_related('serverstatus').all()
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
    处理raid的模块
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



