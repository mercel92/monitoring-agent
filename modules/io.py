import os
import psutil

class IO:

    sections = []

    def  setDiscs(self):

        self.sections = []

        data = psutil.disk_partitions(all=False)
        for part in data:

            if os.name == 'nt':
                if 'cdrom' in part.opts or part.fstype == '':
                    continue

            usage = psutil.disk_usage(part.mountpoint)

            if len(part.mountpoint) > 25:
                continue

            if part.mountpoint.find("home/virtfs") != -1:
                continue

            if part.mountpoint == '/boot/efi' :
                continue

            disc = {}
            disc['Device']  = part.device
            disc['Mount']   = part.mountpoint
            disc['Total']   = usage.total
            disc['Free']    = usage.free
            disc['Used']    = usage.used
            disc['Percent'] = usage.percent
            disc['Inode']   = self.getInode(part.device)

            self.sections.append(disc)

    def getInode(self,path):

        df_out = [s.split() for s in os.popen('/bin/df -khi -P '+path).read().splitlines()]
        data = df_out[1:][0]
        inode = {}
        inode['Filesystem'] = data[0]
        inode['Inodes']     = data[1]
        inode['IUsed']      = data[2]
        inode['IFree']      = data[3]
        inode['IUse']       = data[4]
        inode['Mounted']    = data[5]

        return inode


    def getDiscs(self):
        return self.sections

    def getIoStats(self):

        result = psutil.disk_io_counters();
        obj = {
            "ReadCount": result.read_count,
            "WriteCount": result.write_count,
            "ReadBytes": result.read_bytes,
            "WriteBytes": result.write_bytes,
            "ReadTime": result.read_time,
            "WriteTime": result.write_time
        }

        return obj
