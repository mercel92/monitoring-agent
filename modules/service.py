import os,sys,platform
import socket
import subprocess
from subprocess import PIPE, Popen

from modules.memory import Memory
from modules.cpu import Cpu
from modules.io import IO
from modules.server import Server
from modules.network import Network

class Service:

    ps = {}
    data = {}

    def __init__(self,ps):
        self.ps = ps

    def load(self):

        self.loadMemory()
        self.loadCpu()
        self.loadDiscs()
        self.loadServerInfo()
        self.loadNetworkStats()
        self.loadServiceStatus()
        self.data['LoadAvg'] = os.getloadavg()

        self.data['Cpanel'] = { 'Version' : self.shellexec(['cat', '/usr/local/cpanel/version'], False)}
        self.data['LiteSpeed'] = {
            "Version": self.shellexec(['cat', '/usr/local/lsws/VERSION'], False),
            "Serial": self.shellexec(['cat', '/usr/local/lsws/conf/serial.no'], False),
            "Expdate": self.shellexec('/usr/local/lsws/bin/lshttpd -V | grep -m 1 "Leased"', True)
        }

        phpVersion  = (subprocess.Popen("php -v", shell=True, stdout=subprocess.PIPE).stdout.read()[:30])
        if self.isV3() == True:
            phpVersion = phpVersion.decode('utf-8')

        self.data['Php'] = {'Version' :phpVersion}

        return self.data


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
