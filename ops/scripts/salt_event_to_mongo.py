#!/bin/env python
#coding=utf8

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
client = MongoClient()
db = client.salt

# define collection in mongo
key = db.salt_key
grains = db.salt_grains
job = db.salt_job
job_new = db.salt_job_new
job_ret = db.salt_job_ret
error = db.salt_error

# Create Mysql connect
import MySQLdb
mysql_db = MySQLdb.connect("192.168.3.168","ops","ops@123","opsdb" )
cursor = mysql_db.cursor()

# create re pattern objects according to event type
pattern_auth = re.compile(r'salt/auth')
pattern_minion_start = re.compile(r'salt/minion/.+/start')
pattern_key = re.compile(r'salt/key')
pattern_job = re.compile(r'salt/job/.+')
# pattern_job_new = re.compile(r'salt/job/\d+/new')
# pattern_job_ret = re.compile(r'salt/job/\d+/ret/.+')
# pattern_job_prog = re.compile(r'salt/job/\d+/prog/.+/.+')

# Listen Salt Master Event System
event = salt.utils.event.MasterEvent(__opts__['sock_dir'])
for eachevent in event.iter_events(full=True):
	try:
		if pattern_job.match(eachevent['tag']):
			if eachevent['data']['fun'] == "saltutil.find_job":
				continue
			else:
				if eachevent['data'].has_key('id') and eachevent['data'].has_key('return'):
					if eachevent['data']['fun'] == 'grains.items':
						grains.find_one_and_replace({'id':eachevent['data']['id']},eachevent['data'],upsert=True)
						sql = '''INSERT IGNORE INTO system (system_id,create_time,update_time) VALUES (%s,%s,%s)'''
						try:
						   # 执行sql语句
						   cursor.execute(sql,(eachevent['data']['id'],eachevent['data']['_stamp'],eachevent['data']['_stamp']))
						   # 提交到数据库执行
						   mysql_db.commit()
						except Exception as e:
							# raise e
							# Rollback in case there is any error
							mysql_db.rollback()
					job_ret.insert_one(eachevent['data'])
				elif eachevent['data'].has_key('minions'):
					job_new.insert_one(eachevent['data'])
				else:
					job_ret.insert_one(eachevent['data'])
		elif pattern_key.match(eachevent['tag']) or pattern_auth.match(eachevent['tag']):
			key.find_one_and_replace({'id':eachevent['data']['id']},eachevent['data'],upsert=True)
		else:
			continue
	except Exception as e:
		# raise e
		continue


