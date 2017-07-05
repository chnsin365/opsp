# FAQ about cobbler
### xmlrpclib.Fault: <Fault 1: "<class 'cobbler.cexceptions.CX'>:'login failed'">
解决方法：
```
service cobblerd restart
cobbler get-loaders
```

### apr_sockaddr_info_get() failed for cobbler
解决方法：
```
vi /etc/hosts
cobbler_ip fqdn hostname
```

### PXE-E32:TFTP open timeout TFTP"Open"
查找PXE启动芯片出错代码表，是说tftp没有运行,请求没有应答
解决方法：验证TFTP服务是否正在运行
```
service xinetd restart
netstat -nlatup | grep 69

udp        0      0 0.0.0.0:69                  0.0.0.0:*                               6621/xinetd
```

### Cobbler 安装状态获取 ###
通过cobbler status命令可以获取安装进度
```
[root@cobbler ~]# cobbler status
ip             |target              |start            |state            
192.168.3.125  |system:linux        |Fri Jun 30 11:31:29 2017|unknown/stalled  
192.168.3.151  |system:test         |Mon Jul  3 11:13:05 2017|finished         
192.168.3.154  |system:test         |Mon Jul  3 11:26:47 2017|installing (0m 16s)
192.168.3.39   |system:xyz          |Tue Jun 27 15:46:36 2017|finished         
[root@cobbler ~]# cobbler status
ip             |target              |start            |state            
192.168.3.125  |system:linux        |Fri Jun 30 11:31:29 2017|unknown/stalled  
192.168.3.151  |system:test         |Mon Jul  3 11:13:05 2017|finished         
192.168.3.154  |system:test         |Mon Jul  3 11:26:47 2017|finished         
192.168.3.39   |system:xyz          |Tue Jun 27 15:46:36 2017|finished   
```

也可以通过查看/var/log/cobbler/install.log获取

> https://github.com/cobbler/cobbler/issues/1261
