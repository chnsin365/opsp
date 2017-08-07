# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render,redirect
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from opsdb.models import ServiceHost
import time
import nmap
# connect mongodb
try:
	from pymongo import MongoClient
	salt_mongo = get_object_or_404(ServiceHost,service='salt_mongo')
	client = MongoClient(salt_mongo.ip,int(salt_mongo.port))
except Exception as e:
	# raise e
	pass

# config apscheduler
from pytz import utc
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor

# the function is called for apscheduler.add_job()
def test():
	client.cron.testcol.insert_one({'name':'wei.yang'})

def scanner(hosts,ports,arguments='-sV'):
	def callback_result(host, scan_result):
		if scan_result['nmap']['scanstats']['uphosts']:
			doc = {'hosts':hosts,'scan_result':scan_result}
			client.cron.scanner.find_one_and_replace({'host':host},doc,upsert=True)
	try:
		nma = nmap.PortScannerAsync()
		nma.scan(hosts=hosts, ports=ports, arguments=arguments, callback=callback_result)
	except Exception as e:
		print str(e)

jobstores = {
	'default': MongoDBJobStore(collection='jobs', database='cron', client=client)
	# 'mongo': MongoDBJobStore(collection='jobs', database='cron', client=client),
	# 'default': MemoryJobStore()
}
executors = {
	'default': ProcessPoolExecutor(5)
	# 'default': ThreadPoolExecutor(20),
	# 'processpool': ProcessPoolExecutor(5)
}
job_defaults = {
	'coalesce': False,
	'max_instances': 3
}
scheduler = BackgroundScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults, timezone=utc)

try:
	scheduler.start()
except SystemExit:
	client.close()

def cronjobs(request):
	cronjobs = client.cron.joblist.find().sort([('_id',-1)])
	job_list = [job for job in cronjobs]
	page_number =  request.GET.get('page_number')
	if page_number:
	    page_number = int(page_number)
	else:
	    page_number =  10
	paginator = Paginator(job_list, page_number)
	page = request.GET.get('page')
	try:
	    jobs = paginator.page(page)
	except PageNotAnInteger:
	    # If page is not an integer, deliver first page.
	    jobs = paginator.page(1)
	except EmptyPage:
	    # If page is out of range (e.g. 9999), deliver last page of results.
	    jobs = paginator.page(paginator.num_pages)
	return render(request,'cronjob/cronjobs.html',locals())


def add_scanner(request):
	if request.method == 'GET':
		return render(request,'cronjob/add_scanner.html')
	else:
		try:
			hosts = request.POST.get('hosts')
			ports = request.POST.get('ports')
			trigger = request.POST.get('trigger')
			trigger_arg = request.POST.get('trigger_arg')
			job_id = request.POST.get('job_id')
			print hosts,ports,trigger,trigger_arg,job_id
			scheduler.add_job(scanner,trigger,trigger_arg,args=[hosts,ports],id=job_id)
			job = {'name':job_id,'trigger':trigger,'trigger_arg':trigger_arg,\
			'user':request.user.username,'create_time':time.strftime("%Y-%m-%d %X", time.localtime())}
			client.cron.joblist.insert_one(job)
		except Exception as e:
			raise e
		return redirect('cronjob:jobs')	
	
