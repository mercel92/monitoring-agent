#!/usr/bin/python

'''

 * Monitorink Agent 
 * monitorink.com
 * 
 * 
 * @author      Mustafa ERCEL  <mustafa.ercel@tsoft.com.tr>
 * @copyright   Tekrom Teknoloji A.S.
 * @version     1.0
 * @since       Python 2.8

'''

import socket,signal
import time
import json
import subprocess
from subprocess import PIPE, Popen

try:
    import pip
except ImportError:
    print("Please install pip")

try:
    import psutil
except ImportError:
    pip.main(['install', 'psutil'])
    import psutil


from modules.service import Service

sock    = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
Running = True
timeout = 5



def main():

    global timeout,Running,sock

    updateCheckerStart = 5
    updateCheckerTimer = 60
    service     = Service(psutil)
    mainServer  = service.getMainServerIp()
    config      = mainServer.split(':')

    if len(config) < 1:
        print('IP Cozumlenemedi')

    serverConfig = (config[0], int(config[1]))
    connect(serverConfig)

    # dongu patlarsa ?
    signal.signal(signal.SIGTERM, _handle_signal)
    signal.signal(signal.SIGINT, _handle_signal)

    hour = False

    while Running:

        if (updateCheckerStart*timeout) % updateCheckerTimer == 0 :
            print('Checking Update Status')

            updaterStatus = updateChecker()
            if updaterStatus == False :
                subprocess.Popen('python /usr/src/tagent/update.py',shell=True)
                print(' Update.py is executing')

        updateCheckerStart = updateCheckerStart + 1

        obj = {'name' : 'system_info' , 'args' : [ {'data' : {}}]}
        obj['args'] = service.load()

        message = json.dumps(obj)
        try:
            if service.isV3():
                sock.send(message.encode('utf-8'))
            else:
                sock.send(message)

            print('Packet has been sent')

        except:
            print('Packet send event failed')
            sock.close()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            connect(serverConfig)

        time.sleep(timeout)

def _handle_signal(signal, frame):
    global Running
    Running = False

def connect(opts):
    try:
        sock.connect(opts)
    except:
        print('Couldnt connect to server')


def updateChecker():

    try:
        proc = Popen('ps aux | grep tagent/update.py', stdout=PIPE, shell=True)
        process = (proc.communicate()[0])
        update = process.split('\n')
        print(update[0])
        if 'usr/src/tagent/update.py' in update[0]:
            return True
        else:
            return False
    except:
        print('Updater status exception')
        return True


if __name__ == '__main__':
    main()
