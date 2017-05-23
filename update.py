import signal,time,json,os,subprocess,platform

Timeout = 5
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
    print(Hostname)
    r = requests.get(ServiceAddress+Hostname)
    try:
        k = json.loads(r.json())
        print(k)

    except:
        return False

    return False

def main():

    while Running:

        if (checkService() == True):
            try:
                executeScript()
            except:
                print('Sh is not worked')
        else:
            print('No')

        time.sleep(Timeout)

if __name__ == '__main__':
  main()

