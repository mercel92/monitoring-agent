import signal,time,json,os,subprocess,platform, pip

Timeout = 60*1
Running = True
ServiceAddress = 'http://srv.tsoft.club/index/update/'
TriggerFile = './tagent-update.sh'
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
        if len(k) > 0 and k[0]["update"] == True :
            return True
    except:
        return False
    return False

def main():
    while Running:
        if (checkService() == True):
            executeScript()
            print('Sh is  worked')
        else:
            print('Not executed - time ')
        time.sleep(Timeout)
if __name__ == '__main__':
  main()