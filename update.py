import signal,time,json,os,subprocess
from subprocess import Popen, PIPE


Timeout = 5
Running = True
ServiceAddress = 'http://ns991.tekrom.com:9292/servers'
TriggerFile = './simple.sh'

try:
    import requests
except ImportError:
    pip.main(['install', 'requests'])
    import requests

def executeScript():

    global TriggerFile
    print(TriggerFile)
    subprocess.call([TriggerFile])
    print('worked')

def main():
    r = requests.get(ServiceAddress)
    print(r.status_code)

    while Running:
        print('test loop\n')
        executeScript()
        time.sleep(Timeout)

if __name__ == '__main__':
  main()

