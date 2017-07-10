#!/bin/bash
# -*- coding: utf-8 -*-
#
# @author: alex.tang <feng.tang@gmail.com>
# Created on 2017/07/10

curl -L https://bootstrap.saltstack.com -o install_salt.sh
sleep 30
sh install_salt.sh -P
echo "master: 192.168.3.167" >> /etc/salt/monion
service salt-minion restart
