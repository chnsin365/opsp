# -*- coding: utf-8 -*-
###
# author: wei.yang@jinmuinfo.com
###
import requests
import json


class SaltAPI():
    def __init__(self, host, username, password, port=443, auth="pam"):
        self.salt_api_host = host
        self.port = port
        self.username = username
        self.passoword = password
        self.auth = auth
        self.headers = {
            "Accept": "application/json",
            "Content-type": "application/json"
        }
        self.post_data = ""

    def do_post(self, api="login"):
        post_req = requests.post("https://%s:%s/%s" % (self.salt_api_host, self.port, api), data=json.dumps(self.post_data),
                                 headers=self.headers,verify=False)
        return post_req.json()["return"][0]

    def login(self):
        self.post_data = {
            "username": self.username,
            "password": self.passoword,
            "eauth": self.auth
        }
        resp = self.do_post()
        self.token = resp["token"]
        self.expire = resp["expire"]
        return self.token

    def run(self, fun="test.ping", target="*", arg_list=[],expr_form='list'):
        self.post_data = [
            {
                "client": "local",
                "tgt": target,
                "fun": fun,
                "expr_form": expr_form,
                "arg": arg_list,
                "username": self.username,
                "password": self.passoword,
                "eauth": self.auth
            }
        ]
        return self.do_post("run")