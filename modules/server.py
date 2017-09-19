
import psutil
import platform
import time
import socket

class Server:

    def __init__(self):

        self.Hostname           = socket.gethostname()
        self.ActiveUser         = len(psutil.users())
        self.ActiveConnection   = 0
        self.BootTime           = psutil.boot_time()
        self.Date               = time.time()
        self.Ip                 = ''

    def setActiveConnection(self,data):
        self.ActiveConnection = data

    def getIp(self):
        try:
            return socket.gethostbyname(socket.gethostname())
        except:
            return ''


    def get(self):

        data = {}
        data['Hostname']            = self.Hostname
        data['ActiveUser']          = self.ActiveUser
        data['ActiveConnection']    = self.ActiveConnection
        data['Boottime']            = self.BootTime
        data['Date']                = self.Date
        data['IP']                  = self.getIp()
        return data

    def getOs(self):

        data = {}
        data['System']  = platform.system()
        data['Release'] = platform.release()
        data['Dist']    = platform.dist()
        return data

    def __str__(self):
        return 'This object can not be convertable'





