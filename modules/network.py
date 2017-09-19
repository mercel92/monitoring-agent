import psutil
import sys

class Network:

    avg  = 0
    data = {}
    pnic = []

    def stats(self):

        totalData = psutil.net_io_counters()
        total = {}
        total['ByteSend'] = totalData.bytes_sent
        total['ByteReceive'] = totalData.bytes_recv
        total['PacketSend'] = totalData.packets_sent
        total['PacketReceive'] = totalData.packets_recv

        if self.isV3() == True :
            p_net_io = psutil.net_io_counters(pernic=True).items()
        else:
            p_net_io = psutil.net_io_counters(pernic=True).iteritems()

        for attr, value in p_net_io:

            self.pnic.append({
                "Name": attr,
                "ByteSend": totalData.bytes_sent,
                "ByteReceive": totalData.bytes_recv,
                "PacketSend": totalData.packets_sent,
                "PacketReceive": totalData.packets_recv
            })

        return {'avg': total, 'data': self.pnic}

    def isV3(self):

        req_version = (2, 8)
        cur_version = sys.version_info[:2]
        if cur_version >= req_version:
            return True
        return False
