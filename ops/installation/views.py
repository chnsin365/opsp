# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render,redirect
from django.shortcuts import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from .models import *
from opsdb.models import ServiceHost
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import json
from ops.sshapi import remote_cmd
from .raid_api import RAIDAPI
from ops.ipmi_api import ipmitool
from .cobbler_api import CobblerAPI
from .tasks import run_test_suit,get_info_from_vcenter,clone_vm

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
                        'model':server_info['model'],\
                        'power':'on'})
        if created:
            tag = Tag.objects.get(tag_type=server_info['tag'])
            server.tag = tag
            if tag.tag_type == 'L':
                status = ServerStatus.objects.get(status_type='init')
            else:
                status = ServerStatus.objects.get(status_type='running')
            server.serverstatus = status
            server.save()
        nics = server.nic_set.all()
        if nics:
            nics.delete()
        if server_info['nics']:
            for nic in server_info['nics']:
                nic_obj = Nic.objects.create(\
                    mac=nic['mac'],\
                    name=nic['nic_name'],\
                    model=nic['nic_model'])
                nic_obj.server = server
                nic_obj.save()
        disks = server.disk_set.all()
        if disks:
            disks.delete()
        if server_info['disk']:
            for disk in server_info['disk']:
                disk_obj = Disk.objects.create(\
                    path=disk['disk_path'],\
                    dtype=disk['disk_type'],\
                    raid_name=disk['raid_name'],\
                    raid_type=disk['raid_type'],\
                    size=disk['disk_size'])
                disk_obj.server = server
                disk_obj.save()            
    except Exception as e:
        created = e
    return HttpResponse(created)

@csrf_exempt
def install_pre_post(request):
    name = request.POST['name']
    ip = request.POST['ip']
    progress = request.POST['progress']
    print name,ip,progress
    try:
        PreSystem.objects.filter(hostname=name,ip=ip).update(progress=progress)
        ret = True
    except Exception as e:
        ret = False
    return HttpResponse(ret)

def init(request):
    status = get_object_or_404(ServerStatus,status_type='init')
    server_list = status.server_set.all()
    page_number =  request.GET.get('page_number')
    if page_number:
        page_number = int(page_number)
    else:
        page_number =  10
    paginator = Paginator(server_list, page_number)
    page = request.GET.get('page')
    try:
        servers = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        servers = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        servers = paginator.page(paginator.num_pages)
    return render(request,'installation/init.html',locals())

def install(request):
    system_list = PreSystem.objects.all()
    page_number =  request.GET.get('page_number')
    if page_number:
        page_number = int(page_number)
    else:
        page_number =  10
    paginator = Paginator(system_list, page_number)
    page = request.GET.get('page')
    try:
        systems = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        systems = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        systems = paginator.page(paginator.num_pages)    
    return render(request,'installation/install.html',locals())

def server(request):
    return render(request,'installation/server.html',locals())

def server_detail(request,server_id):
    server = get_object_or_404(Server,pk=server_id)
    return render(request,'installation/server_detail.html',locals())

def server_delete(request):
    ids = request.GET.get('ids','').lstrip(',')
    ids = ids.split(',')
    ret_data = {}
    for server_id in ids:
        try:
            get_object_or_404(Server,pk=server_id).delete()
        except Exception as e:
            ret_data[server_id] = str(e)
    return HttpResponse(json.dumps(ret_data))

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
        Server.objects.filter(pk=server_id).update(**kwargs)
        return redirect('installation:server_edit',server_id)

def init_cobbler(id=1):
    cobbler = get_object_or_404(Cobbler,pk=id)
    if cobbler:
        url = "http://%s/cobbler_api"%(cobbler.ip)
        user = cobbler.user
        password = cobbler.password
        cblr = CobblerAPI(url,user,password)
    return cblr

def server_change_status(request):
    ids = request.GET.getlist('ids[]','')
    status = request.GET.get('status')
    cobbler = init_cobbler()
    ret = {}
    for server_id in ids:
        server = get_object_or_404(Server,pk=server_id)
        try:
            pre_system = server.presystem
            result = cobbler.del_system(pre_system.hostname)
            if result['result']:
                status = get_object_or_404(ServerStatus,status_type=status)
                server.serverstatus = status
                if server.presystem.progress == 1:
                    ipmi_ip = server.ipmi_ip
                    ipmi_user = server.ipmi_user
                    ipmi_pass = server.ipmi_pass
                    if not (ipmi_ip and ipmi_user and ipmi_pass):
                        ret = "ipmi地址、用户名或密码为空"
                    else:
                        ipmi = ipmitool(ipmi_ip,ipmi_pass,username=ipmi_user)
                        ipmi.chassis_status()
                        if ipmi.error:
                            ret = ipmi.error
                        else:
                            ipmi.boot_to_pxe()
                            ipmi.chassis_reboot()
                            server.power = 'start'
                pre_system.delete()
                server.save()
            else:
                ret[server_id] = result['comment']
        except Exception as e:
            # raise e
            ret[server_id] = str(e)
    return HttpResponse(json.dumps(ret))

def select_cab(request):
    idc_id = request.GET.get('idc_id','')
    cabs = Cabinet.objects.filter(idc_id=idc_id)
    result = {}
    for cab in cabs:
        result[cab.id] = cab.name
    return HttpResponse("%s"%(json.dumps(result)))

def server_raid(request,server_id,fun,array):
    '''
    raid模块,包含以下方法：
    1、查看物理硬盘状态 (raid_status)
    2、创建raid (create_raid)
    3、删除raid (delete_raid)
    '''
    server = get_object_or_404(Server,pk=server_id)
    addr = server.pxe_ip
    if fun == 'raid_status':
        disks = server.disk_set.all()
        values = disks.values('raid_name','raid_type').distinct()
        rds = dict()
        for value in values:
            tmp = {}
            tmp['raid_type'] = value['raid_type']
            dks = disks.filter(raid_name=value['raid_name'])
            dk = []
            for d in dks:
                dk.append({'path':d.path,'dtype':d.dtype,'size':d.size})
            tmp['disks'] = dk
            rds[value['raid_name']] = tmp
    elif fun == 'create_raid':
        if request.method == 'GET':
            disks = server.disk_set.filter(raid_name='Unassigned')
            return render(request,'installation/create_raid.html',locals())
        else:
            disks = request.POST.getlist('drivers','')
            drivers = ','.join(disks)
            raid_type = request.POST.get('raid_type','')
            rd = RAIDAPI(server,addr,user='root',passwd='P@ssw0rd')
            ret_data = rd.create_raid(drivers,raid_type)
            if ret_data['status']:
                cobbler = get_object_or_404(ServiceHost,service='cobbler')
                cmd ="curl -L http://%s:%s/cobbler/svc/post_server_info.sh | sh > /tmp/curl.log 2>&1"%(cobbler.ip,cobbler.port)
                try:
                    ret = remote_cmd(cmd,addr,user='root',passwd='P@ssw0rd')
                    if ret['status']:
                        ret_data['result'] = 'Raid %s has been created on %s'%(raid_type,drivers)
                    else:
                        ret_data['result'] = ret['result']
                except Exception as e:
                    ret_data['result'] = str(e)
            else:
                pass
            return HttpResponse(ret_data['result'])
    elif fun == 'delete_raid':
        rd = RAIDAPI(server,addr,user='root',passwd='P@ssw0rd')
        ret_data = rd.delete_raid(array)
        if ret_data['status']:
            cobbler = get_object_or_404(ServiceHost,service='cobbler')
            cmd ="curl -L http://%s:%s/cobbler/svc/post_server_info.sh | sh > /tmp/curl.log 2>&1"%(cobbler.ip,cobbler.port)
            try:
                ret = remote_cmd(cmd,addr,user='root',passwd='P@ssw0rd')
                if ret['status']:
                    ret_data['result'] = 'Array %s has been deleted'%(array)
                else:
                    ret_data['result'] = ret['result']
            except Exception as e:
                ret_data['result'] = str(e)
        else:
            pass
        return HttpResponse(json.dumps(ret_data))
    else:
        pass
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
    if not (ipmi_ip and ipmi_user and ipmi_pass):
        ret_data = "error"
    else:
        ipmi = ipmitool(ipmi_ip,ipmi_pass,username=ipmi_user)
        ipmi.chassis_status()
        if ipmi.error:
            ret_data = ipmi.error
        else:  
            try:
                if fun == 'chassis_off':
                    if 'off' in ipmi.output:
                        pass
                    else:
                        ipmi.chassis_off()
                    server.power = 'off'
                elif fun == 'install':
                    if 'off' in ipmi.output:
                        ipmi.boot_to_pxe()
                        ipmi.chassis_on()
                    else:
                        ipmi.boot_to_pxe()
                        ipmi.chassis_reboot()
                    server.presystem.progress = 0
                    server.presystem.save()
                elif fun == 'boot_to_pxe':
                    if 'on' in ipmi.output:
                        pass
                    else:
                        ipmi.boot_to_pxe()
                        ipmi.chassis_on()
                    server.power = 'start'         
                else:
                    pass
                server.save()
            except Exception as e:
                ret_data = str(e)
    return HttpResponse(ret_data)

def update_ipmi(request,server_id):
    if request.method == "GET":
        server = get_object_or_404(Server,pk=server_id)
        ret_data = "用户或密码错误,请重新配置"
        return render(request,'installation/update_ipmi.html',locals())
    else:
        kwargs = {}
        for k,v in request.POST.dict().items():
            if k == 'csrfmiddlewaretoken':
                pass
            else:
                if v:
                    kwargs[k] = v
        ipmi = ipmitool(kwargs['ipmi_ip'],kwargs['ipmi_pass'],username=kwargs['ipmi_user'])
        ipmi.chassis_status()
        ret_data = ipmi.output
        if 'socket' in ret_data:
            ret_data = 'ipmi地址错误或网络错误'
        elif 'Error' in ret_data:
            ret_data = 'ipmi账号或密码错误'
        else:
            Server.objects.all().update(**kwargs)
            ret_data = '账号配置成功'
        return render(request,'installation/msg.html',locals())

def cobbler(request):
    cobbler_list = Cobbler.objects.all()
    page_number =  request.GET.get('page_number')
    if page_number:
        page_number = int(page_number)
    else:
        page_number =  10
    paginator = Paginator(cobbler_list, page_number)
    page = request.GET.get('page')
    try:
        cobblers = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        cobblers = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        cobblers = paginator.page(paginator.num_pages)    
    return render(request,'installation/service_conf.html',locals())

def edit_cobbler(request,id):
    cobbler = get_object_or_404(Cobbler,pk=id)
    if request.method == "GET":
        return render(request,'installation/edit_cobbler.html',locals())
    else:
        ip = request.POST.get('ip','')
        user = request.POST.get('user','')
        password = request.POST.get('password','')
        try:
            cobbler.ip = ip
            cobbler.user = user
            cobbler.password = password
            cobbler.save()
            messages.success(request, '更新成功')
        except Exception as e:
            messages.error(request, str(e))
        return render(request,'installation/edit_cobbler.html',locals())

def add_cobbler(request):
    if request.method == "GET":
        return render(request,'installation/add_cobbler.html')
    else:
        ip = request.POST.get('ip','')
        user = request.POST.get('user','')
        password = request.POST.get('password','')
        try:
            cobbler,created = Cobbler.objects.get_or_create(ip=ip,defaults={'user':user,'password':password})
            if created:
                messages.success(request, '添加成功')
            else:
                messages.error(request, 'IP地址重复，请更换IP。')
        except Exception as e:
            messages.error(request, str(e))
            return render(request,'installation/add_cobbler.html')
        return redirect('installation:edit_cobbler',cobbler.id)

def get_system(request,server_id):
    server = get_object_or_404(Server,pk=server_id)
    cobbler = init_cobbler()
    ret_data = cobbler.find_system(server.pxe_mac)
    if not ret_data['result']:
        messages.error(request, ret_data['comment'])
    return render(request,'installation/config_sys.html',locals())

def add_system(request,server_id):
    server = get_object_or_404(Server,pk=server_id)
    # cobbler = CobblerAPI("http://192.168.3.166/cobbler_api","admin","admin")
    cobbler = init_cobbler()
    if request.method == 'GET':
        profiles = cobbler.get_proflies()
        if 'result' in profiles:
            messages.error(request, profiles['comment'])
            return render(request,'installation/install.html',locals())
        else:       
            return render(request,'installation/add_system.html',locals())
    else:
        hostname = request.POST.get('hostname','')
        ip_addr = request.POST.get('ip_addr','')
        mac_addr = request.POST.get('mac_addr','')
        profile = request.POST.get('profile','')
        kopts = request.POST.get('kopts','')
        try:
            ret_data = cobbler.add_system(hostname,ip_addr,mac_addr,profile,kopts)
            if ret_data['result']:
                PreSystem.objects.get_or_create(ip=ip_addr,defaults={'profile':profile,'server_id':server.id,'hostname':hostname})
                status = get_object_or_404(ServerStatus,status_type='install')
                server.serverstatus = status
                server.save()
        except Exception as e:
            messages.error(request, e)
            profiles = cobbler.get_proflies()
            return render(request,'installation/add_system.html',locals())
        return redirect('installation:get_system',server_id)

def view_system(request,system):
    # cobbler = CobblerAPI("http://192.168.3.166/cobbler_api","admin","admin")
    cobbler = init_cobbler()
    system = cobbler.get_system(system)
    ret_data = json.dumps(json.loads(json.dumps(system), parse_int=str), indent=4, sort_keys=False, ensure_ascii=False)
    return render(request,'installation/tips.html',locals())

def edit_system(request,server_id,system):
    server = get_object_or_404(Server,pk=server_id)
    pre_system = get_object_or_404(PreSystem,hostname=system)
    # cobbler = CobblerAPI("http://192.168.3.166/cobbler_api","admin","admin")
    cobbler = init_cobbler()
    if request.method == 'GET':
        profiles = cobbler.get_proflies()
        if 'result' in profiles:
            messages.error(request, profiles['comment'])
            return render(request,'installation/install.html',locals())
        else:       
            return render(request,'installation/edit_system.html',locals())
    else:
        hostname = request.POST.get('hostname','')
        ip_addr = request.POST.get('ip_addr','')
        mac_addr = request.POST.get('mac_addr','')
        profile = request.POST.get('profile','')
        kopts = request.POST.get('kopts','')
        try:
            ret_data = cobbler.edit_system(system,hostname,ip_addr,mac_addr,profile,kopts)
            if ret_data['result']:
                PreSystem.objects.update_or_create(server_id=server_id,\
                    defaults={'ip':ip_addr,'profile':profile,'server_id':server.id,'hostname':hostname})
        except Exception as e:
            messages.error(request, e)
            profiles = cobbler.get_proflies()
            return render(request,'installation/edit_system.html',locals())
        return redirect('installation:get_system',server_id)

def delete_system(request,system,server_id):
    # cobbler = CobblerAPI("http://192.168.3.166/cobbler_api","admin","admin")
    cobbler = init_cobbler()
    ret_data = cobbler.del_system(system)
    return redirect('installation:get_system',server_id)

def tasks(request):
    '''
    for celery test
    '''
    print('before run_test_suit')
    result = run_test_suit.delay('110')
    print('after run_test_suit')
    if result.ready():
        print result.get()
    else:
        print result,type(result)
    return HttpResponse("job is runing background~")

def vcenter(request):
    vcenters = Vcenter.objects.all()
    datastores = Datastore.objects.all()
    datacenters = Datacenter.objects.all()
    clusters = Cluster.objects.all()
    hosts = Host.objects.all()
    guests = Guest.objects.all()
    return render(request,'installation/vcenter.html',locals())

def add_vcenter(request):
    if request.method == "GET":
        return render(request,'installation/add_vcenter.html')
    else:
        name = request.POST.get('name','')
        ip = request.POST.get('ip','')
        port = request.POST.get('port','')
        user = request.POST.get('user','')
        password = request.POST.get('password','')
        try:
            vcenter,created = Vcenter.objects.get_or_create(name=name,ip=ip,user=user,defaults={'password': password,'port':port})
            if created:
                result = get_info_from_vcenter.delay(vcenter.id,user,password,ip,port=port)
                messages.success(request, '添加成功')
            else:
                messages.error(request, 'IP地址重复，请更换IP。')
        except Exception as e:
            messages.error(request, str(e))
            return render(request,'installation/add_vcenter.html')
        return redirect('installation:vcenter')

def edit_vcenter(request,id):
    vcenter = get_object_or_404(Vcenter,pk=id)
    if request.method == "GET":
        return render(request,'installation/edit_vcenter.html',locals())
    else:
        try:
            name = request.POST.get('name','')
            ip = request.POST.get('ip','')
            user = request.POST.get('user','')
            password = request.POST.get('password','')
            vcenter = Vcenter.objects.update(name=name,ip=ip,user=user,password=password)
            messages.success(request, '更新成功')
        except Exception as e:
            messages.success(request, str(e))
        return render(request,'installation/edit_vcenter.html',locals())

def delete_vcenter(request,id):
    try:
        Vcenter.objects.filter(pk=id).delete()
        ret = ''
    except Exception as e:
        ret = str(e)
    return HttpResponse(ret)

def add_vm(request):
    '''
    create vm from tempate
    '''
    if request.method == "GET":
        vcenters = Vcenter.objects.all()
        templates = Guest.objects.filter(is_template=True)
        return render(request,'installation/add_vm.html',locals())
    else:
        vcenter_name = request.POST['vcenter']
        vcenter = get_object_or_404(Vcenter,name=vcenter_name)
        vm_name = request.POST['vm_name']
        template = request.POST['template']
        vm_cpus = request.POST['vm_cpus']
        vm_cpu_sockets = request.POST['vm_cpu_sockets']
        vm_memory = request.POST['vm_memory']
        datacenter_name = request.POST['datacenter']
        datastore_name = request.POST['datastore']
        cluster_name = request.POST['cluster']
        power_on = request.POST['power']
        try:
            result = clone_vm.delay(vcenter.id,vcenter.ip,vcenter.user,vcenter.password,vcenter.port,\
                template,vm_name,datacenter_name,datastore_name,cluster_name,power_on,vm_cpus,\
                vm_cpu_sockets, vm_memory)
        except Exception as e:
            raise e
        return redirect('installation:vcenter')

def get_obj(request):
    val = request.GET.get('val','')
    obj_type = request.GET.get('type','')
    result = {}
    if obj_type == 'vc':
        vc = Vcenter.objects.get(name=val)
        dcs = vc.datacenter_set.all()
        for dc in dcs:
            result[dc.name] = dc.name
    elif obj_type == 'dc':
        dc = Datacenter.objects.get(name=val)
        clusters = dc.cluster_set.all()
        for cluster in clusters:
            result[cluster.name] = cluster.name
    elif obj_type == 'cluster':
        cluster = Cluster.objects.get(name=val)
        hosts = cluster.host_set.all()
        for host in hosts:
            result[host.ip] = host.ip
    elif obj_type == 'ds':
        vc = Vcenter.objects.get(name=val)
        dses = vc.datastore_set.all()
        for ds in dses:
            result[ds.name] = ds.name
    else:
        result = {'-1':'Nothing'}
    return HttpResponse(json.dumps(result))






