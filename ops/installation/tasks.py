#!/usr/bin/env python 
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals
from celery import shared_task
import time
from .models import Vcenter,Datastore,Datacenter,Cluster,Host,Guest,Vnet,Server,ServerStatus
from .getvmsbycluster import get_vms_by_cluster
from .getdatastorebyname import get_ds_from_vcenter
from .clone_vm import create_vm_by_template
# from celery import task

# @task
@shared_task
def run_test_suit(ts_id):
	'''
	Just for test
	'''
	print "++++++++++++++++++++++++++++++++++++"
	print('jobs[ts_id=%s] running....' % ts_id)
	time.sleep(10.0)
	print('jobs[ts_id=%s] done' % ts_id)
	result = "this is a test message"
	return result

@shared_task
def get_info_from_vcenter(vc_id,user,password,ip,port=443):
	'''
	return vms by cluster
	'''
	vc = Vcenter.objects.get(pk=vc_id)
	vcenter = get_vms_by_cluster(user,password,ip,port)
	if vcenter:
		for datacenter,clusters in vcenter.items():
			dc,created = Datacenter.objects.get_or_create(name=datacenter)
			if dc:
				dc.vcenter = vc
				dc.save()
				for cluster,hosts in clusters.items():
					clu,created = Cluster.objects.get_or_create(name=cluster)
					if clu:
						clu.datacenter = dc
						clu.save()
						for host,vms in hosts.items():
							ht,created = Host.objects.get_or_create(ip=host)
							if ht:
								ht.cluster = clu
								status = ServerStatus.objects.get(status_type='running')
								try:
									server = Server.objects.get(prod_ip=host,serverstatus_id=status.id)
									ht.server = server
									ht.save()
								except Exception as e:
									# raise e
									pass
								for name,vm in vms.items():
									guest,created = Guest.objects.update_or_create(name=name,\
										defaults={'annotation':vm['annotation'],\
										'cpu':vm['cpu'],\
										'diskGB':vm['diskGB'],\
										'folder':vm['folder'],\
										'mem':vm['mem'],\
										'ostype':vm['ostype'],\
										'status':vm['state'],\
										'is_template':vm['is_template']})

									if guest:
										l = vm['path'].split()
										dt = l[0].strip('[]')
										ds,created = Datastore.objects.get_or_create(name=dt,vcenter_id=vc.id)
										if ds:
											guest.datastore = ds
											datastore = get_ds_from_vcenter(ds.name,user,password,ip,port)
											if datastore:
												ds.capacity = datastore.get('capacity','')
												ds.free_space = datastore.get('free_space','')
												ds.provisioned = datastore.get('provisioned','')
												ds.free_space = datastore.get('capacity','')
												ds.uncommitted = datastore.get('uncommitted','')
												ds.hosts = datastore.get('hosts','')
												ds.vms = datastore.get('vms','')
												ds.save()
										guest.path = l[1]
										guest.host = ht
										guest.save()
										if vm['net']:
											for mac,net in vm['net'].items():
												vnet,created = Vnet.objects.get_or_create(mac=mac)
												vnet.connected = net.get('connected','')
												vnet.ip = net.get('ip','')
												vnet.netlabel = net.get('netlabel','')
												vnet.prefix = net.get('prefix','')
												vnet.guest = guest
												vnet.save()

@shared_task
def clone_vm(vcenter_ip,vcenter_user,vcenter_password,vcenter_port,template,vm_name,\
	datacenter_name,datastore_name,cluster_name,power_on,vm_cpus, vm_cpu_sockets, vm_memory):
	'''
	clone vm from template
	'''
	create_vm_by_template(vcenter_ip,vcenter_user,vcenter_password,vcenter_port,template,vm_name,\
		datacenter_name,datastore_name,cluster_name,power_on,vm_cpus, vm_cpu_sockets, vm_memory)


