#!/bin/env python
#coding=utf8

'''
author: wei.yang@jinmuinfo.com
date: 2017.07.25

function:
Listening Salt Master Event System and parase the job return ,then store result to mongo and mysql

requirements:
1、The script must be exacuted on salt master because of salt modules
2、The script need pymongo to connect mongodb
3、The script need MySQLdb to connect mysql
'''

# Import python libs
import json
import re
from datetime import datetime

# Import salt modules
import salt.config
import salt.utils.event


__opts__ = salt.config.client_config('/etc/salt/master')

# Create MongoDB connect
from pymongo import MongoClient
client = MongoClient('192.168.3.167',27017)
db = client.salt

# define collection in mongo
# key = db.salt_key
# pend_key = db.salt_auth
grains = db.salt_grains
# job = db.salt_job
# job_new = db.salt_job_new
job_ret = db.salt_job_ret
# error = db.salt_error
job_list = db.salt_joblist

# Create Mysql connect
import MySQLdb
mysql_db = MySQLdb.connect("192.168.3.168","ops","ops@123","opsdb" )
cursor = mysql_db.cursor()

# create re pattern objects according to event type
# pattern_auth = re.compile(r'salt/auth')
# pattern_minion_start = re.compile(r'salt/minion/.+/start')
# pattern_key = re.compile(r'salt/key')
# pattern_job = re.compile(r'^salt/job/')
# pattern_job_new = re.compile(r'salt/job/\d+/new')
pattern_job_ret = re.compile(r'salt/job/\d+/ret/.+')
# pattern_job_prog = re.compile(r'salt/job/\d+/prog/.+/.+')

# Listen Salt Master Event System
event = salt.utils.event.MasterEvent(__opts__['sock_dir'])
for eachevent in event.iter_events(full=True):
	try:
		if pattern_job_ret.match(eachevent['tag']):
			if eachevent['data']['fun'] == "saltutil.find_job":
				if eachevent['data'].has_key('return') and eachevent['data']['return'].has_key('metadata'):
					job_list.update_one({'metadata':eachevent['data']['return']['metadata']},\
									{"$set": {"state_id":eachevent['data']['return']['jid']}})
				else:
					continue
			else:
				if eachevent['data'].has_key('id') and eachevent['data'].has_key('return'):
					if eachevent['data']['fun'] == 'grains.items':
						sql = '''INSERT INTO system (system_id,ip,os,num_cpus,mem_total,power_status,minion_status,is_delete,create_time,update_time)\
						 VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE ip=%s,os=%s,num_cpus=%s,mem_total=%s,power_status=%s,minion_status=%s,is_delete=%s'''
						try:
						    # 执行sql语句
							cursor.execute(sql,(eachevent['data']['id'],\
						   	eachevent['data']['return']['fqdn_ip4'][0],\
						   	' '.join([eachevent['data']['return']['osfullname'],\
						   		eachevent['data']['return']['osrelease']]),\
						   	str(eachevent['data']['return']['num_cpus']),\
						   	("%.2f"%(eachevent['data']['return']['mem_total']/1024.0)),True,True,False,\
						   	eachevent['data']['_stamp'],\
						   	eachevent['data']['_stamp'],\
						   	eachevent['data']['return']['fqdn_ip4'][0],\
						   	' '.join([eachevent['data']['return']['osfullname'],\
						   		eachevent['data']['return']['osrelease']]),\
						   	str(eachevent['data']['return']['num_cpus']),\
						   	("%.2f"%(eachevent['data']['return']['mem_total']/1024.0)),True,True,False))
						    # 提交到数据库执行
							mysql_db.commit()
						except Exception as e:
							# raise e
							# Rollback in case there is any error
							mysql_db.rollback()
						grains.find_one_and_replace({'id':eachevent['data']['id']},eachevent['data'],upsert=True)
					elif re.match(r'.*salt\s+.+\s+state\.sls\s+(.+)',eachevent['data']['fun_args'][0]):
						m = re.match(r'.*Failed:\s+(\d+).*',eachevent['data']['return'],re.DOTALL)
						if m:
							faild_count = int(m.groups()[0])
							if faild_count:
								job_list.update_one({'jid':eachevent['data']['jid']},\
									{"$set": {"status":'Failed','progress':'Finish'}})
							else:
								job_list.update_one({'jid':eachevent['data']['jid']},\
									{"$set": {"status":'Success','progress':'Finish'}})
						else:
							job_list.update_one({'jid':eachevent['data']['jid']},\
									{"$set": {"status":'Failed','progress':'Finish'}})
					else:
						pass
					job_ret.insert_one(eachevent['data'])
				else:
					continue
		else:
			continue
	except Exception as e:
		print str(e)
		# continue
