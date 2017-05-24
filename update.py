import signal,time,json,os,subprocess,platform, pip
##test##test
Timeout = 60*1
Running = True
ServiceAddress = 'http://srv.tsoft.club/index/update/'
TriggerFile = '/usr/src/tagent/tagent-update.sh'
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
        time.sleep(Timeout)
        if (checkService() == True):
            executeScript()
            print('Sh is  worked update is stopped')
            break
        else:
            print('Not executed - time ')

if __name__ == '__main__':
  main()
