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
