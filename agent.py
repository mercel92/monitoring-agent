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
running = True
timeout = 5

def main():

    global timeout,running,sock

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

    while running:

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


if __name__ == '__main__':
    main()