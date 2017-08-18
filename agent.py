#!/usr/bin/python
# -*- coding: utf-8 -*-
# mustafa.ercel@tsoft.com.tr
import socket, signal
import sys, os, platform, re
import json, time
import calendar, datetime, sqlite3
import subprocess
from subprocess import PIPE, Popen

## socket emit timeout
SocketRefreshTime = 5
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


def cleanup():
    print("Cleaning up ...")


def detectIp():
    global NodeServerIp
    fname = '/usr/src/tagent/server_ip.txt'
    try:
        with open(fname) as f:
            NodeServerIp = f.read()
            NodeServerIp = NodeServerIp.replace('\n', '')
    except:
        print('Ip file cannot read')


def main():
    global Running
    global SocketRefreshTime
    global sock
    global NodeServerIp

    detectIp()

    EConfig = NodeServerIp.split(':')
    if len(EConfig) < 1:
        print('IP Cozumlenemedi')

    ServerConfig = (EConfig[0], int(EConfig[1]))
    connect(ServerConfig)

    # dongu patlarsa ?
    signal.signal(signal.SIGTERM, _handle_signal)
    signal.signal(signal.SIGINT, _handle_signal)

    hour = False

    while Running:

        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        network = networkstats()
        ActiveConnection = (subprocess.Popen("netstat -tuwanp | awk '{print $4}' | sort | uniq -c | wc -l", shell=True,
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
                            "BootTime": psutil.boot_time(),
                            "Date": time.time(),
                            "Ip": detectIpAddr(),
                        },
                        "Os": {
                            "System": platform.system(),
                            "Release": platform.release(),
                            "Dist": platform.dist()
                        },
                        "Php": {
                            "Version": php_version
                        },
                        "Cpanel": {
                            "Version": shellexec(['cat', '/usr/local/cpanel/version'], False)
                        },
                        "LiteSpeed": {
                            "Version": shellexec(['cat', '/usr/local/lsws/VERSION'], False),
                            "Serial": shellexec(['cat', '/usr/local/lsws/conf/serial.no'], False),
                            "Expdate": shellexec('/usr/local/lsws/bin/lshttpd -V | grep -m 1 "Leased"', True)
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
                            "Avg": network['avg'],
                            "Data": network['data']
                        }, "Services": {
                        "Http": scanport(80),
                        "Ssh": scanport(4646),
                    }
                    }
                }
            ]
        }

        # once a hour
        currentHour = datetime.datetime.now().hour
        if(hour == False or currentHour != hour):
            hour = currentHour
            obj['args'].append({'data': getCpanelInfo()})

        message = json.dumps(obj)
        ##print (sys.stderr, 'Sending packet..')
        try:
            if cur_version >= req_version:
                print("Python3.x")
                sock.send(message.encode('utf-8'))

            else:
                print("Python2.x")
                sock.send(message)
            print('Packet has been sent')
        except:
            print('Packet send event failed')
            sock.close()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            connect(ServerConfig)

        time.sleep(SocketRefreshTime)


def _handle_signal(signal, frame):
    global Running
    Running = False
    cleanup()


def detectIpAddr():
    try:
        return socket.gethostbyname(socket.gethostname())
    except:
        return ''


def connect(opts):
    try:
        sock.connect(opts)
    except:
        print('Couldnt connect to server')


def shellexec(args, shell):
    try:
        proc = Popen(args, stdout=PIPE, shell=shell)
        if shell == False:
            return (proc.communicate()[0].split())
        return (proc.communicate()[0])
    except:
        return ''


def disk():
    disks = []
    for part in psutil.disk_partitions(all=False):
        # windows kurulursa ?
        if os.name == 'nt':
            if 'cdrom' in part.opts or part.fstype == '':
                continue
        usage = psutil.disk_usage(part.mountpoint)
        if len(part.mountpoint) > 25:
            break
        if part.mountpoint.find("home/virtfs") != -1:
            break
        obj = {
            "Device": part.device,
            "Mount": part.mountpoint,
            "Total": usage.total,
            "Free": usage.free,
            "Used": usage.used,
            "Percent": usage.percent
        }  ##
        disks.append(obj)

    return disks


def diskio():
    result = psutil.disk_io_counters();
    obj = {
        "ReadCount": result.read_count,
        "WriteCount": result.write_count,
        "ReadBytes": result.read_bytes,
        "WriteBytes": result.write_bytes,
        "ReadTime": result.read_time,
        "WriteTime": result.write_time
    }

    return obj


def networkstats():
    total = psutil.net_io_counters()
    totalobj = {
        "ByteSend": total.bytes_sent,
        "ByteReceive": total.bytes_recv,
        "PacketSend": total.packets_sent,
        "PacketReceive": total.packets_recv
    }
    pnic = []
    pers = psutil.net_io_counters(pernic=True)

    if cur_version >= req_version:
        p_net_io = psutil.net_io_counters(pernic=True).items()  # itemitems durumu python3 de yok
    else:
        p_net_io = psutil.net_io_counters(pernic=True).iteritems()
    for attr, value in p_net_io:
        pnic.append({
            "Name": attr,
            "ByteSend": total.bytes_sent,
            "ByteReceive": total.bytes_recv,
            "PacketSend": total.packets_sent,
            "PacketReceive": total.packets_recv
        })

    return {'avg': totalobj, 'data': pnic}


def scanport(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = s.connect_ex(('127.0.0.1', port))

    if result == 0:
        s.close()
        return True
    return False


def getCpanelInfo():
    file = '/etc/trueuserdomains'
    if (os.path.exists(file) == True):
        fileObj = open(file, 'r')
        sites = fileObj.readlines()
        siteList = []
        for index, site in enumerate(sites):
            site = site.replace(' ', '').replace('\n', '')
            pos = site.find(':')
            username  = site[pos:].replace(':', '')
            bandwidth = getBandwithFromDomain(username)

            if(bandwidth == False):
                bandwidth = -1;

            siteList.append({'domain': site[:pos], 'username': username, 'bandwidth' : bandwidth})
        return siteList
    return False


def getMailCount():
    logList = []
    file = '/var/log/exim_mainlog'
    if (os.path.exists(file) == True):
        logs = subprocess.Popen(
            "grep 'cwd=/home' /var/log/exim_mainlog | awk ' {print $3} ' | cut -d / -f 3 | sort -bg | uniq -c | sort -bg",
            shell=True, stdout=subprocess.PIPE).stdout.readlines()
        for index, log in enumerate(logs):
            log = log.strip().replace('\n', '')
            regexObj = re.search('\d+ {1}[A-Za-z0-9]{1}', log)
            pos = regexObj.end() - 1
            logList.append({'username': log[pos:], 'count': int(log[:pos])})
        return logList
    return False


def getBandwithFromDomain(user):
    now = datetime.datetime.now()
    monthRanges = calendar.monthrange(now.year, now.month)
    s1 = str(monthRanges[0]) + '/' + str(now.month) + '/' + str(now.year)
    timestamp = time.mktime(datetime.datetime.strptime(s1, "%d/%m/%Y").timetuple())

    bandwidth = 0
    file = '/var/cpanel/bandwidth/' + user + '.sqlite'

    if (os.path.exists(file) == False):
        return False

    conn = sqlite3.connect(file)
    c = conn.cursor()

    sqlQuery = 'SELECT SUM(bytes) AS sum  FROM \'bandwidth_5min\' WHERE unixtime >' + str(timestamp)
    c.execute(sqlQuery)
    bandwidth = c.fetchone()[0]
    conn.close()

    return bandwidth;


if __name__ == '__main__':
    main()
