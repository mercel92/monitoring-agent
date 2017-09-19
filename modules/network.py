import psutil
import sys

class Network:

    avg  = 0
    data = {}

    def __init__(self):
        self.data = psutil.net_io_counters()

    def stats(self):

        total = {}
        total['ByteSend']       = self.data.bytes_sent
        total['ByteReceive']    = self.data.bytes_recv
        total['PacketSend']     = self.data.packets_sent
        total['PacketReceive']  = self.data.packets_recv

        if self.isV3() == True :
            p_net_io = psutil.net_io_counters(pernic=True).items()
        else:
            p_net_io = psutil.net_io_counters(pernic=True).iteritems()

        parts = self.getPartitionStats(p_net_io)
        return {'avg': total, 'data': parts}

    def getPartitionStats(self,data):

        pnic = []
        for attr, value in data:
            pnic.append({
                "Name": attr,
                "ByteSend":0,
                "ByteReceive": 0,
                "PacketSend": 0,
                "PacketReceive": 0
            })
        return pnic

    def isV3(self):

        req_version = (2, 8)
        cur_version = sys.version_info[:2]
        if cur_version >= req_version:
            return True
        return False
