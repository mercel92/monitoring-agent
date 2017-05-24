import signal,time,json,os,subprocess,platform, pip,logging
##sonupdate
Timeout = 60*60
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

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    handler = logging.FileHandler('/usr/src/tagent/updatepy.log')
    handler.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    while Running:
        time.sleep(Timeout)
        if (checkService() == True):
            logger.info('Files updated.Update.py stopped.Script Executed.Success !')
            executeScript()
            print('Sh is  worked update is stopped')
            break
        else:
            logger.info('Agent update time has not yet.Update.py is working.. ')
            print('Not executed - time ')

if __name__ == '__main__':
  main()
