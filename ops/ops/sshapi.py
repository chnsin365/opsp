#!/usr/bin/python
import paramiko

def remote_cmd(cmd,host,user='root',passwd='P@ssw0rd'):
	try:
		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh.connect(hostname=host,username=user,password=passwd)
		stdin,stdout,stderr = ssh.exec_command(cmd)
		return stdout.read()
	except Exception as e:
		return str(e)
	finally:
		ssh.close()

def put_file(user,passwd,localpath,remotepath):
	try:
		t = paramiko.Transport((hostname,22))
		t.connect(username=user,password=passwd)
		sftp = paramiko.SFTPClient.from_transport(t)
		sftp.put(localpath,remotepath)
	except Exception as e:
		print str(e)