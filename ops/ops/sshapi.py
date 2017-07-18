#!/usr/bin/python
import paramiko

def remote_cmd(cmd,host,port=22,user='root',passwd='P@ssw0rd'):
	ret = {'status':True,'result':'','err':''}
	try:
		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh.connect(hostname=host,port=port,username=user,password=passwd,timeout=30)
		stdin,stdout,stderr = ssh.exec_command(cmd)
		ret['result'] = stdout.read()
		ret['err'] = stderr.read()
	except Exception as e:
		ret = {'status':False,'result':str(e)}
	finally:
		ssh.close()
		return ret

def put_file(user,passwd,localpath,remotepath):
	try:
		t = paramiko.Transport((hostname,22))
		t.connect(username=user,password=passwd)
		sftp = paramiko.SFTPClient.from_transport(t)
		sftp.put(localpath,remotepath)
	except Exception as e:
		print str(e)