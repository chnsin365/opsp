#!/usr/bin/env python 
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals
from celery import shared_task
import time
from celery import task


# @task()
@shared_task
def add(x, y):
    return x + y

# @task
@shared_task
def run_test_suit(ts_id):
    print "++++++++++++++++++++++++++++++++++++"
    print('jobs[ts_id=%s] running....' % ts_id)
    time.sleep(10.0)
    print('jobs[ts_id=%s] done' % ts_id)
    result = True
    return result