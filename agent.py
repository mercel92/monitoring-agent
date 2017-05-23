#!/usr/bin/python
# -*- coding: utf-8 -*-
#chmod
import socket, signal
import sys, os, platform
import json, time
import subprocess

## chmod git update
## tcp server config
## socket emit timeout
SocketRefreshTime = 2
## client
NodeServerIp = ''

try:
    import pip
except ImportError:
    print("Please install pip")

try:
    import psutil
except ImportError:
    pip.main(['install', 'psutil'])
    import psutil

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

Running = True

req_version = (2, 8)  # Kıyaslayacağımız python versiyon
cur_version = sys.version_info[:2]  # Kullanılan python versiyonu

print("cur_version", cur_version)


def cleanup():
    print ("Cleaning up ...")


def detectIp():
    global NodeServerIp
    fname = './server_ip.txt'
    try:
        with open(fname) as f:
            NodeServerIp = f.read()
            NodeServerIp = NodeServerIp.replace('\n','')
    except:
        print('Ip file cannot read')

def main():
    global Running
    global SocketRefreshTime
    global sock
    global NodeServerIp

    detectIp()
    ServerConfig = (NodeServerIp.split(':'))
    connect(ServerConfig)


    # dongu patlarsa ?
    signal.signal(signal.SIGTERM, _handle_signal)
    signal.signal(signal.SIGINT, _handle_signal)

    while Running:
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        network = networkstats()
        ActiveConnection = (subprocess.Popen("netstat -tuwanp | awk '{print $4}' | sort | uniq -c | wc -l",
                                             shell=True,
                                             stdout=subprocess.PIPE).stdout.read())
        php_version = (subprocess.Popen("php -v", shell=True, stdout=subprocess.PIPE).stdout.read()[:30])
        if cur_version >= req_version:
            # pyhton 3.x >
            ActiveConnection = ActiveConnection.decode('utf-8').replace('\n', '')
            php_version = php_version.decode('utf-8')
        # Send emit
        obj = {
            'name': 'system_info',
            'args': [
                {"data":
                    {
                        "System": {
                            "Hostname": socket.gethostname(),
                            "ActiveUser": len(psutil.users()),

                            "ActiveConnection": ActiveConnection,
                            "BootTime"	: psutil.boot_time(),
                            "Date"			  : time.time(),
                            "Ip" : socket.gethostbyname(socket.gethostname()),
                        } ,"Os" : {
                            "System" :platform.system(),
                        "Release": platform.release(),
                        "Dist" :platform.dist()
                    },
                        "Php": {
                            "Version": php_version
                        },
                        "Cpanel": {
                            "Version": cpanel()
                        },
                        "Cpu": {
                            "Avg": psutil.cpu_percent(interval=1),
                            "Count": psutil.cpu_count()
                        },
                        "Memory": {
                            "Free": memory.free,
                            "Used": memory.used,
                            "Total": memory.total,
                            "Percent": memory.percent
                        },
                        "Swap": {
                            "Free": swap.free,
                            "Used": swap.used,
                            "Total": swap.total,
                            "Percent": swap.percent
                        },
                        "LoadAvg": os.getloadavg(),
                        "Disc": disk(),
                        "IO": diskio(),
                        "Network": {
                            "Avg"  	: network['avg'],
                            "Data" 		: network['data']
                        },"Services" : {
                            "Http" : scanport(80),
                            "Ssh"  : scanport(4646),
                        }
                    }
                }
            ]
        }

        message = json.dumps(obj)
        ##print (sys.stderr, 'Sending packet..')
        try :
            if cur_version >= req_version:
                print("Python3.x")
                sock.send(message.encode('utf-8'))

            else:
                print("Python2.x")
                sock.send(message)
            print ('Packet has been sent')
        except :
            print ('Packet send event failed')
            sock.close()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            connect(ServerConfig)

        time.sleep(SocketRefreshTime)


def _handle_signal(signal, frame):

    global Running
    Running = False
    cleanup()

def connect (opts):

    try :sock.connect(opts)
    except :
        print ('Couldnt connect to server')

def cpanel() :

    try:
        return subprocess.Popen("cat /usr/local/cpanel/version", stdout=subprocess.PIPE).stdout.read().replace('\n' ,'')
    except:
        return ''

def disk() :
    disks = []
    for part in psutil.disk_partitions(all=False):
        # windows kurulursa ?
        if os.name == 'nt':
            if 'cdrom' in part.opts or part.fstype == '':
                continue
        usage = psutil.disk_usage(part.mountpoint)
        obj = {
            "Device"  : part.device,
            "Mount"   : part.mountpoint,
            "Total"	  : usage.total,
            "Free" 	  : usage.free,
            "Used"	  :usage.used,
            "Percent" :usage.percent
        }
        disks.append(obj)

    return disks

def diskio() :

    result = psutil.disk_io_counters();
    obj = {
        "ReadCount"  : result.read_count,
        "WriteCount" : result.write_count,
        "ReadBytes"	 : result.read_bytes,
        "WriteBytes" : result.write_bytes,
        "ReadTime"   : result.read_time,
        "WriteTime"  : result.write_time
    }

    return obj

def networkstats():

    total  = psutil.net_io_counters()
    totalobj  = {
        "ByteSend" : total.bytes_sent,
        "ByteReceive" : total.bytes_recv,
        "PacketSend" : total.packets_sent,
        "PacketReceive" : total.packets_recv
    }
    pnic  = []
    pers  = psutil.net_io_counters(pernic=True)

    if cur_version >= req_version:
        p_net_io =  psutil.net_io_counters(pernic=True).items()  # itemitems durumu python3 de yok
    else:
        p_net_io = psutil.net_io_counters(pernic=True).iteritems()
    for attr, value in p_net_io:
        pnic.append({
            "Name"	: attr,
            "ByteSend" : total.bytes_sent,
            "ByteReceive" : total.bytes_recv,
            "PacketSend" : total.packets_sent,
            "PacketReceive" : total.packets_recv
        })

    return {'avg' : totalobj,  'data' : pnic }

def scanport(port):

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = s.connect_ex(('127.0.0.1', port))

    if result == 0:
        s.close()
        return True
    return False

if __name__ == '__main__':
  main()
