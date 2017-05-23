import signal,time,json,os,subprocess

Timeout = 5
Running = True
ServiceAddress = 'http://ns991.tekrom.com:9292/servers'
TriggerFile = ''

try:
    import requests
except ImportError:
    pip.main(['install', 'requests'])
    import requests

def executeScript():

    shellscript = subprocess.Popen([TriggerFile], stdin=subprocess.PIPE)
    shellscript.stdin.write("yes is worked\n")
    shellscript.stdin.close()
    returncode = shellscript.wait()  # blocks until shellscript is done

    for line in shellscript.stdout.readlines():
        print(line)


def main():
    r = requests.get(ServiceAddress)
    print(r.status_code)

    while Running:
        print('test loop\n')
        executeScript()
        time.sleep(Timeout)

if __name__ == '__main__':
  main()

