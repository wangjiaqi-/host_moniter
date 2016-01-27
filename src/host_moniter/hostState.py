'''
Created on 2015.9.10

@author: wjq
'''
import urllib
import MySQLdb
import time
import json
import re
from time import sleep

hostname='localhost'

def get_host_info():
    hostname='localhost'

    host = json.loads(urllib.urlopen('http://'+hostname+':4567/_status/_list').read())
    result = dict()
    error = False
    for h in host:
        cpu = json.loads(urllib.urlopen('http://'+hostname+':4567/_status/'+h+'/_services/CPU Percent').read())
        cpu_per = 0
        if 'OK' or 'WARNING' or 'CRITICAL' in cpu:
            try:
                cpu_per = re.search(r"\d+%", cpu['plugin_output']).group()
                cpu_per= float(cpu_per[0: cpu_per.__len__()-1])
            except:
                error = True
        else:
            error = True
        Logger.log_normal('cpu---------'+str(error))

        disk = json.loads(urllib.urlopen('http://'+hostname+':4567/_status/'+h+'/_services/Root Partition').read())
        disktotal=diskper=diskused=diskfree=0
        if 'OK' or 'WARNING' or 'CRITICAL' in disk:
            try:
                disktotal = float(re.search(r"\d+", disk['plugin_output']).group())
                diskper = re.search(r"\d+%", disk['plugin_output']).group()
                diskper = 100-float(diskper[0: diskper.__len__()-1])
                diskused = disktotal*diskper*0.01
                diskfree = disktotal-diskused
            except:
                error = True
        else:
            error = True
        Logger.log_normal('disk---------'+str(error))

        mem = json.loads(urllib.urlopen('http://'+hostname+':4567/_status/'+h+'/_services/Memory Usage').read())
        memdata = 0
        if 'OK' or 'WARNING' or 'CRITICAL' in mem:
            try:
                memdata = re.search(r"-?\d+(\.\d+)?%", mem['plugin_output']).group()
                memdata = float(memdata[0: memdata.__len__()-1])
            except:
                error = True
        else:
            error = True
        Logger.log_normal('memory---------'+str(error))

        net = json.loads(urllib.urlopen('http://'+hostname+':4567/_status/'+h+'/_services/Bandwidth Usage').read())
        net_bandwidth=0
        if 'OK' or 'WARNING' or 'CRITICAL' in net:
            try:              
                pat = re.compile(r"\d+\.\d+")
                netdata = re.findall(pat,net['plugin_output'])
                net_bandwidth = float(netdata[2])
            except:
                error = True
        else:
            error = True
        Logger.log_normal('bandwidth---------'+str(error))

        value=[h, h, cpu_per, disktotal, diskused, diskfree, diskper, memdata, net_bandwidth]
        result[h]=value, error
    return result

def write_to_db(values):
    conn = MySQLdb.connect(host='localhost', user='root', passwd='')
    cur = conn.cursor()
    conn.select_db('deploy')
    Logger.log_high('inserting into database...')
    for k in values:
        values[k].append(time.strftime('%Y-%m-%d %H:%M:%S'))
        cur.execute('insert into hosts values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', values[k])
        print values[k]
        conn.commit()
    cur.close()
    conn.close()
        
def main():
    while True:
        values = dict()
        error = True
        for i in range(3):
            Logger.log_normal(time.strftime('%Y-%m-%d %H:%M:%S'))
            result = get_host_info()
            for k in result:    
                if result[k][1] == True:
                    pass
                else:
                    values[k] = result[k][0]
                    error = False
            sleep(600)
        if error == False:
            write_to_db(values)
        else:
            Logger.log_fail(time.strftime('%Y-%m-%d %H:%M:%S') + 'fail to insert into database')
    

class Logger:                                                                      
        HEADER = '\033[95m'                                                        
        OKBLUE = '\033[94m'                                                        
        OKGREEN = '\033[92m'                                                       
        WARNING = '\033[93m'                                                       
        FAIL = '\033[91m'                                                          
        ENDC = '\033[0m'                                                           
                                                                                   
        @staticmethod                                                              
        def log_normal(info):                                                      
                print Logger.OKBLUE + info + Logger.ENDC                           
                                                                                   
        @staticmethod                                                              
        def log_high(info):                                                        
                print Logger.OKGREEN + info + Logger.ENDC                          
                                                                                   
        @staticmethod                                                              
        def log_fail(info):                                                        
                print Logger.FAIL + info + Logger.ENDC    