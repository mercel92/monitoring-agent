
import psutil

class Cpu:

    def __init__(self):
        self.avg   = 0
        self.count = 0

    def setAvg(self,data):
        self.avg = data

    def setCount(self,data):
        self.count = data

    def getAvg(self):
        self.avg = psutil.cpu_percent(interval=1)
        return self.avg

    def getCount(self):
        self.count = psutil.cpu_count()
        return self.count

    def get(self):
        return ''

    def __str__(self):
        return 'This object can not be convertable'





