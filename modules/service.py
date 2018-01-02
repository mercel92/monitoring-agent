import os,sys,platform,datetime
import socket
import subprocess
from subprocess import PIPE, Popen

from modules.memory import Memory
from modules.cpu import Cpu
from modules.io import IO
from modules.server import Server
from modules.network import Network
from modules.cpanel import Cpanel

class Service:

    ps = {}
    data = {}
    all  = []
    hour = False

    def __init__(self,ps):
        self.ps = ps

    def load(self):

        self.loadMemory()
        self.loadCpu()
        self.loadDiscs()
        self.loadServerInfo()
        self.loadNetworkStats()
        self.loadServiceStatus()
        self.loadMailData()
        self.loadTasks()

        self.data['LoadAvg'] = os.getloadavg()

        self.data['Cpanel'] = { 'Version' : self.shellexec(['cat', '/usr/local/cpanel/version'], False)}

        self.data['LiteSpeed'] = {
            "Version": self.shellexec(['cat', '/usr/local/lsws/VERSION'], False),
            "Serial":  self.shellexec(['cat', '/usr/local/lsws/conf/serial.no'], False),
            "Expdate": self.shellexec('/usr/local/lsws/bin/lshttpd -V | grep -m 1 "Leased"', True)
        }

        self.data['Services']['LiteSpeed'] = False;
        if self.data['LiteSpeed']['Version'] != '' :
            self.data['Services']['LiteSpeed'] = self.scanport(7080)

        phpVersion  = (subprocess.Popen("php -v", shell=True, stdout=subprocess.PIPE).stdout.read()[:30])
        if self.isV3() == True:
            phpVersion = phpVersion.decode('utf-8')

        self.data['Php'] = {'Version' :phpVersion}

        self.all = [{ 'data' : self.data}]
        # once a hour  test
        currentHour = datetime.datetime.now().hour
        if(self.hour == False or currentHour != self.hour):
            self.hour = currentHour
            cpanel = Cpanel()
            domainInfo = cpanel.getCpanelInfo()
            self.all.append({'data' : domainInfo})

        return self.all

    def loadTasks(self):

        self.data['Tasks'] = {
            'task_total' : 0,
            'task_running' : 0 ,
            'task_sleeping' : 0,
            'task_stopped' :0,
            'task_zombie' : 0
        }

        output = self.shellexec('top - b - n 1 - d 0 | grep Tasks:', True)

        if output != '' :
            output = output.split()
            k = [int(s) for s in output if s.isdigit()]
            self.data['Tasks']['task_total']    = k[0]
            self.data['Tasks']['task_running']  = k[1]
            self.data['Tasks']['task_sleeping'] = k[2]
            self.data['Tasks']['task_stopped']  = k[3]
            self.data['Tasks']['task_zombie']   = k[4]


        return

    def loadMailData(self):

        self.data['Email'] = {
            'QueueCount': 0,
            'QueueArray': [],
        }

        output = self.shellexec('exim -bp | exiqsumm',True)
        if output != '':
            arr = output.split()
            y = [s for s in arr if '---' not in s]
            f = lambda arr, n=5: [arr[i:i + n] for i in range(0, len(arr), n)]
            arr = f(y)
            self.data['Email']['QueueCount']  = arr[-1][0]
            self.data['Email']['QueueArray']  = arr

        return

    def loadMemory(self):

        memory = Memory()
        self.data['Memory'] = memory.getMemory()
        self.data['Swap'] = memory.getSwap()
        return

    def loadCpu(self):

        cpu = Cpu()
        self.data['Cpu'] = {}
        self.data['Cpu']['Avg'] = cpu.getAvg()
        self.data['Cpu']['Count'] = cpu.getCount()
        return

    def loadDiscs(self):

        input  = IO()
        input.setDiscs()
        self.data['Disc'] = input.getDiscs()
        self.data['IO']   = input.getIoStats()
        return

    def loadServerInfo(self):

        server = Server()

        connections = (subprocess.Popen("netstat -tuwanp | awk '{print $4}' | sort | uniq -c | wc -l", shell=True,stdout=subprocess.PIPE).stdout.read())
        if self.isV3() == True:
            connections = connections.decode('utf-8').replace('\n', '')

        server.setActiveConnection(connections)
        self.data['System'] = server.get()
        self.data['Os'] = server.getOs()
        return

    def loadNetworkStats(self):

        network = Network()
        data = network.stats()

        self.data['Network'] = {}
        self.data['Network']['Avg']  = data['avg']
        self.data['Network']['Data'] = {} ##data['data']
        return

    def loadServiceStatus(self):

        self.data['Services'] = {}
        self.data['Services']['Http'] = self.scanport(80)
        self.data['Services']['Https']  = self.scanport(443)
        self.data['Services']['Mysql']  = self.scanport(3306)
        self.data['Services']['Litespeed']  = self.scanport(7080)
        self.data['Services']['Ssh']  = self.scanport(4646)

        return


    def shellexec(self,args, shell):
        try:
            proc = Popen(args, stdout=PIPE, shell=shell)
            if shell == False:
                return (proc.communicate()[0].split())
            return (proc.communicate()[0])
        except:
            return ''


    def scanport(self,port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = s.connect_ex(('127.0.0.1', port))

        if result == 0:
            s.close()
            return True
        return False

    def isV3(self):

        req_version = (2, 8)
        cur_version = sys.version_info[:2]
        if cur_version >= req_version:
            return True
        return False

    def getMainServerIp(self):

        ip = ''
        fname = '/usr/src/tagent/server_ip.txt'
        try:
            with open(fname) as f:
                ip = f.read()
                ip = ip.replace('\n', '')
                return ip
        except:
            print('Ip file cannot read')
