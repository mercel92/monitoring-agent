import signal,time

Timeout = 5
Running = False

def main():
    while Running:
        print('test')
        time.sleep(Timeout)

if __name__ == '__main__':
  main()

