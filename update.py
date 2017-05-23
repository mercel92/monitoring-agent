import signal,time,json,os,subprocess,platform, pip

Timeout = 10
Running = True
ServiceAddress = 'http://srv.tsoft.club/index/update/'
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

def checkService() :
    global ServiceAddress
    Hostname = platform.uname()[1]
    r = requests.get(ServiceAddress+Hostname)
    try:
        k = json.loads(r.text)
        print(k[0]['hostname'])
        print(ServiceAddress + Hostname)
    except:
        return False
    return True

def main():
    while Running:
        if (checkService() == True):
            executeScript()
            print('Sh is not worked')
        else:
            print('No')
        time.sleep(Timeout)
if __name__ == '__main__':
  main()