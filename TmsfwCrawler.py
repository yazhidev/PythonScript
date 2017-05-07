# coding=utf-8
import importlib,sys

default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    importlib.reload(sys)
    sys.setdefaultencoding(default_encoding)

import urllib.request
import random
import time
import datetime
import leancloud
from leancloud import Object
from leancloud import LeanCloudError
from bs4 import BeautifulSoup

class GetPage:
    def __init__(self, url):
        self.url = url
        user_agents = [
            'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
            'Opera/9.25 (Windows NT 5.1; U; en)',
            'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
            'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
            'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',
            'Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9',
            "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Ubuntu/11.04 Chromium/16.0.912.77 Chrome/16.0.912.77 Safari/535.7",
            "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:10.0) Gecko/20100101 Firefox/10.0 ",
        ]
        agent = random.choice(user_agents)
        req = urllib.request.Request(self.url)
        req.add_header('User-Agent', agent)
        req.add_header('Host', 'www.tmsf.com')
        req.add_header('Accept', '*/*')
        req.add_header('Referer', self.url)
        req.add_header('GET', url)
        html = urllib.request.urlopen(req)
        page = html.read().decode('utf-8')
        self.page = page


class GetXfInfo:
    def __init__(self, page):
        bs = BeautifulSoup(page)
        html_content_list = bs.find_all('div', class_='pcontent')
        if (html_content_list == None):
            print(u'获取新房数据失败')
            print(u'地址： ' + self.url)

        html_content0 = html_content_list[0].string
        self.getXfAll(html_content0)
        html_content1 = html_content_list[1].string
        self.getCanSell(html_content1)
        html_content2 = html_content_list[2].string
        self.getXfLiving(html_content2)
        self.getXfLivingAverage(html_content2)

    # 新房签约套数
    def getXfAll(self, content):
        index1 = content.find('约')
        index2 = content.find('套')
        getStr = content[index1 + 1:index2]
        self.xfAll = int(getStr)
        print('全市新房签约：' + getStr)

    # 其中住宅签约套数
    def getXfLiving(self, content):
        index0 = content.find('约')
        index1 = content.find('约', index0 + 1)
        index2 = content.find('套')
        getStr = content[index1 + 1:index2]
        self.xfLiving = int(getStr)
        print('签约新房中，住宅签约：' + getStr)

    # 其中住宅签约平均面积
    def getXfLivingAverage(self, content):
        index1 = content.find('为')
        index2 = content.find('平')
        getStr = content[index1 + 1:index2]
        self.average = int(getStr)/self.xfLiving
        print('平均签约面积为：' + str(self.average))

    # 全市可售套数
    def getCanSell(self, content):
        index1 = content.find('为')
        index2 = content.find('套')
        getStr = content[index1 + 1:index2]
        print('杭州全市可售房源为：' + getStr)
        self.canSell = int(getStr)
        return getStr

class GetEsfInfo:
    def __init__(self, page):
        bs = BeautifulSoup(page)
        nr = bs.find('div', class_='nr')
        if (nr == None):
            print(u'获取二手房数据失败')

        content = nr.ul.dt.string
        self.getEsfAll(content)
        self.getEsfLiving(content)

    # 二手房签约套数
    def getEsfAll(self, content):
        index1 = content.find('约')
        index2 = content.find('套')
        getStr = content[index1 + 1:index2]
        print('二手房签约：' + getStr)
        self.esfAll = int(getStr)

    # 其中住宅签约套数
    def getEsfLiving(self, content):
        index0 = content.find('约')
        index1 = content.find('约', index0 + 1)
        index2 = content.find('套')
        index3 = content.find('套', index2 + 1)
        getStr = content[index1 + 1:index3]
        print('住宅签约：' + getStr)
        self.esfLiving = int(getStr)

    # 其中住宅签约平均面具
    def getEsfLivingAverage(self):
        return 0


class GetInfo:
    def __init__(self, time):
        self.time = time

    def star(self):
        while self.time > 20170315:
            if self.query() == False:
                # 数据库存在该日期数据，结束循环
                self.getLastDay()
                print(u'结束循环')
                # continue
                break
            else:
                print(u'时间：' + str(self.time))
                xfUrl = "http://www.tmsf.com/upload/report/mrhqbb/" + str(self.time) + "/xf.html"
                esfUrl = "http://www.tmsf.com/upload/report/mrhqbb/" + str(self.time) + "/esf.html"

                xfPage = GetPage(xfUrl)
                xf = GetXfInfo(xfPage.page)
                time.sleep(3)
                esfPage = GetPage(esfUrl)
                esf = GetEsfInfo(esfPage.page)
                self.saveToLeanCloud(self.time, xf, esf)

                self.getLastDay()

                print(u'休眠')
                time.sleep(3)
                print('\n')

        print(u'结束')

    def getLastDay(self):
        # 转换成时间数组
        timeArray = time.strptime(str(self.time), "%Y%m%d")
        # 转换成时间戳
        myTime = time.mktime(timeArray)
        dateArray = datetime.datetime.utcfromtimestamp(myTime)
        # 重新转换成格式
        newYesTime = dateArray.strftime("%Y%m%d")
        print('获得前一天时间：' + str(newYesTime))
        self.time = int(newYesTime)

    # 查询是否已存在该日期数据
    def query(self):
        QueryObject = leancloud.Object.extend('HouseData')
        query_object = leancloud.Query(QueryObject)
        # 判断日期是否存在
        query_list = query_object.equal_to('time', self.time).find()
        if len(query_list) == 0:
            print(u'数据库没有该日期数据，可上传')
            return True
        else:
            return False

    # 数据存入leancloud
    def saveToLeanCloud(self, time, xf, esf):
        TestObject = Object.extend('HouseData')
        test_object = TestObject()
        test_object.set('time', time)
        test_object.set('can_sell', xf.canSell)
        test_object.set('xf_all', xf.xfAll)
        test_object.set('xf_living', xf.xfLiving)
        test_object.set('xf_living_average', xf.average)
        test_object.set('esf_all', esf.esfAll)
        test_object.set('esf_living', esf.esfLiving)
        try:
            test_object.save()
            print(u'存储成功')
        finally:
            print(u'')




# leancloud初始化，请填入自己的id和key
leancloud.init('', '')
nowTime = time.strftime('%Y%m%d', time.localtime(time.time()))
GetInfo(int(nowTime) - 1).star()
