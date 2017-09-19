import os
import sqlite3
import subprocess
import re
import time,datetime,calendar
from subprocess import PIPE, Popen

class Cpanel:

    def getCpanelInfo(self):

        file = '/etc/trueuserdomains'
        if (os.path.exists(file) == True):
            fileObj = open(file, 'r')
            sites = fileObj.readlines()
            siteList = []

            for index, site in enumerate(sites):
                site = site.replace(' ', '').replace('\n', '')
                pos = site.find(':')
                username = site[pos:].replace(':', '')
                bandwidth = self.getBandwithFromDomain(username)
                quota = self.getQuotaInfoFromDomain(username)

                if (bandwidth == False):
                    bandwidth = -1;

                if (quota == False):
                    quota = {'space': '0', 'limit': '0'}

                siteList.append({'domain': site[:pos], 'username': username, 'bandwidth': bandwidth, 'quota': quota})
            return siteList
        return False

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

    def getQuotaInfoFromDomain(user):


        result = subprocess.Popen("quota -u " + user + " | grep -Eo '[0-9]{6,10}'", shell=True,
                                  stdout=subprocess.PIPE).stdout.readlines()

        response = {}
        if (len(result) > 0):
            response['space'] = result[0].replace('\n', '')
            response['total'] = result[1].replace('\n', '')

            return response
        return False