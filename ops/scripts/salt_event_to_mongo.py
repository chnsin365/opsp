#!/bin/env python
#coding=utf8

# Import python libs
import json
import re

# Import salt modules
import salt.config
import salt.utils.event

# Import third party libs
import pymongo

__opts__ = salt.config.client_config('/etc/salt/master')

# Create MongoDB connect
from pymongo import MongoClient
client = MongoClient()
db = client.salt

# define collection 
key = db.salt_key
grains = db.salt_grains
job = db.salt_job

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
	if pattern_job.match(eachevent['tag']):
		if eachevent['data']['fun'] == "saltutil.find_job":
			continue
		else:
			if eachevent['data'].has_key('id') and eachevent['data'].has_key('return'):
				if eachevent['data']['fun'] == 'grains.items':
					grains.find_one_and_replace({'id':eachevent['data']['id']},eachevent['data'],upsert=True)
			job.insert_one(eachevent['data'])
	elif pattern_key.match(eachevent['tag']) or pattern_auth.match(eachevent['tag']):
		key.find_one_and_replace({'id':eachevent['data']['id']},eachevent['data'],upsert=True)
	else:
		continue