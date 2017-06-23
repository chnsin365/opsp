# 自动化运维平台

## 从github下载开发代码

### 安装git(如果已安装，请跳过改步)
```
yum install git
```

### clone开发代码
```
git clone https://github.com/uevol/opsp.git
```

## 配置python开发库

### 方法1、直接从网络安装
```
cd opsp/ops/
pip install -r requirements.txt
```

### 方法2、直接从已有环境copy库到新环境
```cd /usr/lib64/python2.7  
mv site-packages site-packages.bak  
mv usr_lib64_python2.7_site-packages.tar /usr/lib64/python2.7  
tar xvf /usr/lib64/python2.7/usr_lib64_python2.7_site-packages.tar  

cd /usr/lib/python2.7  
mv site-packages site-packages.bak  
mv usr_lib_python2.7_site-packages.tar /usr/lib/python2.7  
tar xvf /usr/lib/python2.7/usr_lib_python2.7_site-packages.tar
```

## 配置settings.py文件(根据实际情况修改配置)
```
mv ops/settings.py.template ops/settings.py
```

## 设置数据库

### 如果只是测试，可直接使用内置开发数据库(sqlite3)

#### 修改opsp配置文件settings.py的数据库配置：
```
DATABASES = {  
    'default': { 
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'), 
    }  
} 
```

### for postgresql

#### for pg
su postgres
psql -U postgres 

#### 修改密码：
\password postgres  

#### 创建数据库用户dbuser，并设置密码:
CREATE USER ops WITH PASSWORD 'ops@123';  

#### 创建用户数据库，这里为opsdb，并指定所有者为ops:
CREATE DATABASE ops OWNER ops;  

#### 将opsdb数据库的所有权限都赋予ops，否则ops只能登录控制台，没有任何数据库操作权限:
GRANT ALL PRIVILEGES ON DATABASE opsdb to ops;  

#### 登录数据库
psql -U ops -d opsdb -h 127.0.0.1 -p 5432;  

#### 根据实际修改opsp配置文件settings.py的数据库配置：

```
DATABASES = {  
    'default': { 
    	'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'), 
        'ENGINE': 'django.db.backends.psql',  
        'NAME': 'opsdb',  
        'USER': 'ops',  
        'PASSWORD': 'ops@123',  
        'HOST': '192.168.31.200',  
        'PORT': '5432',  
    }  
} 
```

### for mysql

#### install MySQLdb
rpm -ivh MySQL-python-1.2.5-1.el7.x86_64.rpm

#### create db
create database opsdb default charset=utf8;

#### create user
grant all on opsdb.* to ops@localhost identified by "ops@123";

#### 根据实际修改opsp配置文件settings.py的数据库配置：

```
DATABASES = {  
    'default': { 
        'ENGINE': 'django.db.backends.psql',  
        'NAME': 'opsdb',  
        'USER': 'ops',  
        'PASSWORD': 'opsdb@123',  
        'HOST': 'localhost',  
        'PORT': '3306',  
    }  
} 
```

## 数据库迁移
```cd ops
python manage.py migrate
```

## 初始化数据
```
cd opsp/ops/
python manage.py shell < scripts/init_data.py
```

## 启动服务
```
python manage.py runserver 0.0.0.0:8000
``` 

## 登录
```
http://xxxx.xxxx.xxxx.xxxx:8000  
初始账户及密码：admin/admin@123
```
