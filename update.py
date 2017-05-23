import signal,time,json

Timeout = 5
Running = True

try:
    import requests
except ImportError:
    pip.main(['install', 'requests'])
    import requests

def main():
    r = requests.get('http://ns991.tekrom.com:9292/servers')
    print(r.status_code)

    while Running:
        print('test loop')
        time.sleep(Timeout)

if __name__ == '__main__':
  main()

