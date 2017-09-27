import os
import sqlite3
import subprocess
import re
import time,datetime,calendar

class Cpanel:

    ######
    ##
    ##  Cpaneldeki domainleri tarar
    ##  Bulunan domainlerin verilerini ceker
    ##
    #######

    def getCpanelInfo(self):

        file = '/etc/trueuserdomains'
        if (os.path.exists(file) == True):
            fileObj = open(file, 'r')
            sites = fileObj.readlines()
            return self.getDomainInfo(sites)
        return False

    ######
    ##
    ##  Domainlerin kota ve trafik bilgilerini
    ##  verir
    ##
    #######
    def getDomainInfo(self,sites):

        siteList = []

        for index, site in enumerate(sites):

            site        = site.replace(' ', '').replace('\n', '')
            pos         = site.find(':')
            username    = site[pos:].replace(':', '')
            bandwidth   = self.getBandwithFromDomain(username)
            quota       = self.getQuotaInfoFromDomain(username)

            if (bandwidth == False):
                bandwidth = -1;

            if (quota == False):
                quota = {'space': '0', 'limit': '0'}
            print(siteList)
            siteList.append({'domain': site[:pos], 'username': username, 'bandwidth': bandwidth, 'quota': quota})

        return siteList


    ######
    ##
    ##  Gonderilen Cpanel kullanicisinin
    ##  Trafik Bilgisini verir
    ##
    #######

    def getBandwithFromDomain(self,user):

        now = datetime.datetime.now()
        monthRanges = calendar.monthrange(now.year, now.month)
        s1 = str(monthRanges[0]) + '/' + str(now.month) + '/' + str(now.year)
        timestamp = time.mktime(datetime.datetime.strptime(s1, "%d/%m/%Y").timetuple())

        bandwidth = 0
        file = '/var/cpanel/bandwidth/' + user + '.sqlite'
        if (os.path.exists(file) == False):
            return False

        conn = sqlite3.connect(file)
        c = conn.cursor()

        sqlQuery = 'SELECT SUM(bytes) AS sum  FROM \'bandwidth_5min\' WHERE unixtime >' + str(timestamp)
        c.execute(sqlQuery)
        bandwidth = c.fetchone()[0]
        conn.close()

        return bandwidth;

    ######
    ##
    ##  Gonderilen Cpanel Kullanicisinin
    ##  Kota bilgisini dondurur
    ##
    #######

    def getQuotaInfoFromDomain(self,user):

        data = self.getQuotaInfo(user)
        if(data == False):
            return False
        else:
            obj = { 'quota': {}, 'inode': {}}
            obj['quota']['used'] = data[0]
            obj['quota']['soft'] = data[1]
            obj['quota']['hard'] = data[2]
            obj['inode']['used'] = data[3]
            obj['inode']['soft'] = data[4]
            obj['inode']['hard'] = data[5]
            return obj

    def getQuotaInfo(self,user):

        try:
            out = subprocess.check_output(['quota', '-u', user])
            lines = out.splitlines()
            data = lines[3].split()
            return data
        except:
            return False

    ######
    ##
    ##  Her hesabin gonderdigi mail sayilari
    ##  username : count formatinda tutar
    ##
    #######

    def getMailCount(self):

        logList = []
        file = '/var/log/exim_mainlog'
        if (os.path.exists(file) == True):
            logs = subprocess.Popen(
                "grep 'cwd=/home' /var/log/exim_mainlog | awk ' {print $3} ' | cut -d / -f 3 | sort -bg | uniq -c | sort -bg",
                shell=True, stdout=subprocess.PIPE).stdout.readlines()

            for index, log in enumerate(logs):
                log = log.strip().replace('\n', '')
                regexObj = re.search('\d+ {1}[A-Za-z0-9]{1}', log)
                pos = regexObj.end() - 1
                logList.append({'username': log[pos:], 'count': int(log[:pos])})

            return logList
        return False