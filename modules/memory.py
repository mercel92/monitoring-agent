import psutil

class Memory:

    def __init__(self):
        self.swap   = {}
        self.memory = {}

    def setSwap(self,data):
        self.swap = data

    def setMemory(self,data):
        self.memory = data

    def getSwap(self):

        swap = psutil.swap_memory()
        data = {}
        data['Free']    = swap.free
        data['Used']    = swap.used
        data['Total']   = swap.total
        data['Percent'] = swap.percent
        return data

    def getMemory(self):

        memory = psutil.virtual_memory()
        data = {}
        data['Free']    = memory.free
        data['Used']    = memory.used
        data['Total']   = memory.total
        data['Percent'] = memory.percent
        return data

    def get(self):
        return self.__dict__.values()

    def getMemcacheMemory(self):

        pid = -1;
        for proc in psutil.process_iter():
            if proc.name() == 'memcached':
                pid = proc.pid;
                break

        if pid == -1 :
            return -1;

        process = psutil.Process(pid)
        mem = process.memory_percent()
        return mem;


    def __str__(self):
        return 'This object can not be convertable'





