from django.db import models

from django.db import connection
import time
import pxssh
import paramiko
import os
from datetime import datetime as _datetime
from django.utils.timezone import utc

class Host(models.Model):
    def __init__(self, **kwargs):
        self.name = kwargs.pop("name", "")
        self.ip = kwargs.pop("ip","")
        self.cpu = kwargs.pop("cpu","")
        self.disk_total = kwargs.pop("disk_total","")
        self.disk_used = kwargs.pop("disk_used","")
        self.disk_free = kwargs.pop("disk_free","")
        self.disk_per = kwargs.pop("disk_per","")
        self.mem = kwargs.pop("mem","")
        self.net_bandwidth = kwargs.pop("net_bandwidth","")
        self.time = kwargs.pop("time","")
        
    def add_host(self, hostname, ip, user, password):
        self.deploy_host(ip, password, user)
        file = '/usr/local/nagios/etc/objects/hosts.cfg'
        content = open(file,'rb').read()
        cont = content[0:]
        host = 'define host{\n    use        linux-server\n    hostname        '+hostname+'\n    alias        '+ip+'\n    address        '+ip+'\n    }'
        with open(file, 'wb') as handle:
            handle.write(host)
            handle.write(cont)
        os.system('sudo service nagios stop')
        os.system('wangjiaqi')
        os.system('sudo service nagios reload')
        os.system('sudo /usr/local/nagios/bin/nagios -d /usr/local/nagios/etc/nagios.cfg')
        
    @classmethod
    def get_all(cls):
        cursor = connection.cursor()
        cursor.execute('select distinct name from hosts')
        rs = cursor.fetchall()
        return [Host.get_one(r[0]) for r in rs]
    
    @classmethod
    def get_one(cls, _host):
        cursor = connection.cursor()
        cursor.execute('select * from hosts where name=%s order by time desc', [_host])
        rs = cursor.fetchone()
        exists = False
        if rs[0] > 0:
            exists = True
            return Host(name=rs[0], ip=rs[1], cpu=rs[2], disk_total=rs[3], disk_used=rs[4], 
                        disk_free=rs[5], disk_per=rs[6], mem=rs[7], net_bandwidth=rs[8], time=rs[9])
        if not exists:
            return None
            
    @classmethod
    def get_detail(cls, _host):
        cursor = connection.cursor()
        cursor.execute('select count(1) as t from hosts where name=%s', [_host]) 
        rs = cursor.fetchone()
        exists = False
        if rs[0] > 0:
            exists = True
        if not exists:
            return None
        cursor.execute('select * from hosts where name=%s', [_host])
        rs = cursor.fetchall()
        details = dict()
        cpu = list()
        disk_per = list()
        mem = list()
        net_bandwidth = list()
        times = list()
        hosts = list()
        for r in rs:
            ip=r[1]
            cpu.append(r[2])
            disk_per.append(r[6])
            mem.append(r[7])
            net_bandwidth.append(r[8])
            times.append(r[9].strftime("%Y-%m-%d-%H"))
            hosts.append(Host(name=_host,ip=ip,cpu=r[2],disk_total=r[3],disk_used=r[4],
                              disk_free=r[5],disk_per=r[6],mem=r[7], net_bandwidth=r[8],time=r[9]))
        details['ip']=ip
        details['cpu']=cpu
        details['disk_per']=disk_per
        details['mem']=mem
        details['net_bandwidth'] = net_bandwidth
        details['time']=times
        details['hosts']=hosts
        return details
    
    @classmethod
    def deploy_host(cls, hostname, password, user):
        try:
            s = pxssh.pxssh()
            s.login(hostname, user, password, original_prompt='[$#>]')
            s.sendline ('sudo apt-get install nagios-plugins nagios-nrpe-server sysstat openssl libssl-dev snmp snmpd snmp-mibs-downloader -y')
            index=s.expect('password')
            print index
            if index==0:
                s.sendline(password)
            s.prompt()
            print s.before
            s.logout()
        except pxssh.ExceptionPxssh, e:
            print "pxssh failed on login."
            print str(e)
        
        t=paramiko.Transport(hostname)
        t.connect(username=user, password=password)
        sftp = paramiko.SFTPClient.from_transport(t)
        remote_dir='/home/'+user
        local_dir='/home/wjq/nagios'
        for root,dirs,files in os.walk(local_dir):
            for filespath in files:
                local_file = os.path.join(root,filespath)
                a = local_file.replace(local_dir,'')
                remote_file = os.path.join(remote_dir,a)
                try:
                    sftp.put(local_file,remote_file)
                except Exception,e:
                    sftp.mkdir(os.path.split(remote_file)[0])
                    sftp.put(local_file,remote_file)
                print "upload %s to remote %s" % (local_file,remote_file)
            for name in dirs:
                local_path = os.path.join(root,name)
                a = local_path.replace(local_dir,'')
                remote_path = os.path.join(remote_dir,a)
                try:
                    sftp.mkdir(remote_path)
                    print "mkdir path %s" % remote_path
                except Exception,e:
                    print e    
        t.close()
        
        try:
            s = pxssh.pxssh()
            s.login (hostname, user, password, original_prompt='[$#>]')
            s.sendline ('sudo cp /home/'+user+'/nrpe.cfg /etc/nagios/')
            index=s.expect('password')
            print index
            if index==0:
                s.sendline(password)
            s.prompt()
            s.sendline ('sudo cp /home/'+user+'/nagios/check_cpu.sh /home/'+user+'/nagios/check_memory.pl /usr/lib/nagios/plugins')
            index=s.expect('password')
            print index
            if index==0:
                s.sendline(password)
            s.prompt()
            s.sendline ('sudo cp /home/'+user+'/nagios/snmpd.conf /etc/snmp/')
            index=s.expect('password')
            print index
            if index==0:
                s.sendline(password)
            s.prompt()
            print s.before
            s.sendline('sudo service nagios-nrpe-server restart')
            index=s.expect('password')
            print index
            if index==0:
                s.sendline(password)
            s.prompt()
            s.sendline('sudo service snmpd restart')
            index=s.expect('password')
            print index
            if index==0:
                s.sendline(password)
            s.prompt()
            print s.before
            s.logout()
        except pxssh.ExceptionPxssh, e:
            print "pxssh failed on login."
            print str(e)
            
            
class APITest(models.Model):
    group   = models.CharField(max_length=20, null=False)
    url = models.CharField(max_length=100, null=False)
    err_no  = models.IntegerField(default=0)
    err_msg = models.CharField(max_length=100, null=False)
    time    = models.DateTimeField(default = _datetime.now())
    
class APITestTime(models.Model):
    time = models.DateTimeField(default = _datetime.now())
    status = models.IntegerField(default=1)