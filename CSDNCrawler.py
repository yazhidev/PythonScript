# coding=utf-8
import importlib,sys

default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    importlib.reload(sys)
    sys.setdefaultencoding(default_encoding)

import urllib.request
import re
import random
import time
from bs4 import BeautifulSoup
import leancloud
from leancloud import Object
from leancloud import LeanCloudError

WAIT_URL = None  # 检测到如果有下一篇，则先保留该网址，等到遍历上一篇结束后，重新回来遍历下一篇
SEARCH_TYPE = 1  # 1为下一篇


class Get_First_Url:
    def __init__(self, url2):
        self.url = url2
        print('\n')
        print('开始获取第一篇博客地址')
        print('博客主页地址： ' + self.url)
        '''
        这是注释
        '''
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
        req.add_header('Host', 'blog.csdn.net')
        req.add_header('Accept', '*/*')
        req.add_header('Referer', 'http://blog.csdn.net/mangoer_ys?viewmode=list')
        req.add_header('GET', url)
        html = urllib.request.urlopen(req)
        page = html.read().decode('utf-8')
        self.page = page
        self.beginurl = self.getFirstUrl()

    # 得到其博客主页的第一篇文章
    def getFirstUrl(self):
        bs = BeautifulSoup(self.page)
        html_content_list = bs.find('span', class_='link_title')
        self.type = 1
        if (html_content_list == None):
            html_content_list = bs.find('h3', class_='list_c_t')  # 不同的主题
            self.type = 2
            if (html_content_list == None):
                return "nourl"

        try:
            return 'http://blog.csdn.net' + html_content_list.a['href']
        finally:
            return ""


class CSDN_Blog_Spider:
    def __init__(self, url2, type):
        self.url = url2
        self.type = type
        if type == 4:
            global WAIT_URL
            WAIT_URL = url2
            print('已记录待爬下一篇地址' + url2)
            print('正在爬取网页地址： ' + self.url)
        else:
            print('正在爬取网页地址： ' + self.url)
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
        req.add_header('Host', 'blog.csdn.net')
        req.add_header('Accept', '*/*')
        req.add_header('Referer', 'http://blog.csdn.net/mangoer_ys?viewmode=list')
        req.add_header('GET', url)
        html = urllib.request.urlopen(req)
        page = html.read().decode('utf-8')
        self.page = page
        self.articalid = self.getArticleId()
        self.authorid = self.getAuthorId()
        self.linkurl = self.getLinkUrl()
        self.blogname = self.getBlogName()
        self.title = self.getTitle()
        print('文章标题是 ' + self.title)
        self.content = self.getContent()
        self.time = self.getTime()
        self.imgurl = self.getImg()
        if self.query():
            self.saveToLeanCloud()

    # 获取文章id
    def getArticleId(self):
        location = -1
        locationList = []
        isStop = True
        while isStop:
            location = self.url.find('/', location + 1)
            if location == -1:
                isStop = False
            else:
                locationList.append(location)

        artical_id = self.url[(locationList[-1] + 1):]
        return artical_id

    # 获取文章link url
    def getLinkUrl(self):
        location = -1
        locationList = []
        isStop = True
        while isStop:
            location = self.url.find('/', location + 1)

            if location == -1:
                isStop = False
            else:
                locationList.append(location)

        link_url = self.url[locationList[2]:]
        return link_url

    # 获得作者id
    def getAuthorId(self):
        location = -1
        locationList = []
        isStop = True
        while isStop:
            location = self.url.find('/', location + 1)

            if location == -1:
                isStop = False
            else:
                locationList.append(location)

        # 第二次和第三次斜杠之间
        author_id = self.url[(locationList[2] + 1):locationList[3]]
        return author_id

    def getTitle(self):
        bs = BeautifulSoup(self.page)

        location = -1
        locationList = []
        isStop = True
        while isStop:
            location = bs.title.string.find('-', location + 1)

            if location == -1:
                isStop = False
            else:
                locationList.append(location)
        # 截取倒数第三次横杆出现前面的字符
        new_title = bs.title.string[:locationList[-3]]
        return new_title.strip()

    def getBlogName(self):
        bs = BeautifulSoup(self.page)
        if self.type == 2:
            html_content_list = bs.find_all('h2', class_='blog_l_t')
            return html_content_list[0].string
        else:
            html_content_list = bs.find('a', href=('http://blog.csdn.net/' + self.authorid))
            return str(html_content_list.string)

    def getTime(self):
        bs = BeautifulSoup(self.page)
        if (self.type == 2):
            html_content_list = bs.findAll('div', class_='date')
            newtime = html_content_list[0].span.string + '-' + html_content_list[0].em.string
            html_content_list = bs.findAll('div', class_='date_b')
            new_time = newtime + '-' + html_content_list[0].string
            return new_time
        else:
            html_content_list = bs.find('span', class_='link_postdate')
            return str(html_content_list.string)

    def getImg(self):
        bs = BeautifulSoup(self.page)
        blog_userface_list = bs.find('div', id='blog_userface')
        if (blog_userface_list == None):
            blog_userface_list = bs.find('div', class_='mess')

        try:
            return blog_userface_list.img['src']
        finally:
            print("")

    def getContent(self):
        bs = BeautifulSoup(self.page)
        html_content_list = bs.findAll('div', {'id': 'article_content', 'class': 'article_content'})
        if (html_content_list == None or len(html_content_list) == 0):
            html_content_list = bs.find_all('div', {'id': 'article_content', 'class': 'skin_detail'})
        html_content = str(html_content_list[0])
        content = html_content
        if '$numbering.append' in content:
            location = -1
            locationList = []
            isStop = True
            while isStop:
                location = content.find('script', location + 1)  # script

                if location == -1:
                    isStop = False
                else:
                    locationList.append(location)

            mylenth = len(locationList)
            newContent = content[:(locationList[mylenth - 3] - 1)] + content[(locationList[mylenth - 1] + 7):]
        else:
            newContent = content

        return newContent

    # 查询是否存在该文章
    def query(self):
        QueryObject = leancloud.Object.extend('CSDNBlogList')
        query_object = leancloud.Query(QueryObject)
        # 先判断文章id是否存在
        query_list = query_object.equal_to('articleid', self.articalid).find()
        if len(query_list) == 0:
            print('数据库没有，可上传')
            return True
        elif query_list[0].get('authorid') == self.authorid:  # 再判断是否等于数据库中该文章的作者id
            print('数据库数据重复')
            return False
        elif query_list[0].get('blogname') == '':
            print('标题为空，可上传')
            return True

    # 数据存入leancloud
    def saveToLeanCloud(self):
        TestObject = Object.extend('CSDNBlogList')
        test_object = TestObject()
        test_object.set('authorid', self.authorid)
        test_object.set('articleid', self.articalid)
        test_object.set('title', self.title)
        test_object.set('blogname', self.blogname)
        test_object.set('content', self.content)
        test_object.set('time', self.time)
        test_object.set('img', self.imgurl)
        try:
            test_object.save()
            print('存储成功')
        finally:
            print("")

    def saveFile(self):
        outfile = open(r'D:\123.txt', 'a')
        outfile.write(self.title)

    def getNextArticle(self):
        bs2 = BeautifulSoup(self.page)
        html = bs2.find('li', class_='prev_article')
        if html == None:
            print('没有上一篇')
            return None
        else:
            return None  # 不读取上一篇，直接去往下遍历读取最新的文章(注释掉这句则会读取上一篇)
            print('有上一篇，地址：' + 'http://blog.csdn.net' + html.a['href'])
            return 'http://blog.csdn.net' + html.a['href']

    def getLastArticle(self):  # 下一篇
        bs2 = BeautifulSoup(self.page)
        html = bs2.find('li', class_='next_article')
        if html == None:
            WAIT_URL = None
            print('没有下一篇')
        else:
            print('有下一篇，地址：' + 'http://blog.csdn.net' + html.a['href'])
            WAIT_URL = 'http://blog.csdn.net' + html.a['href']

    def getLastArticleUrl(self):  # 下一篇
        bs2 = BeautifulSoup(self.page)
        html = bs2.find('li', class_='next_article')
        if html == None:
            print('没有下一篇')
            return None
        else:
            print('有下一篇，地址：' + 'http://blog.csdn.net' + html.a['href'])
            return 'http://blog.csdn.net' + html.a['href']


class Scheduler:
    def __init__(self, url):
        self.start_url = url

    def start(self):
        global WAIT_URL
        #  读取云端存储的关注列表 --start
        Todo = leancloud.Object.extend('CSDNReadList')
        query = Todo.query
        query_list = query.find()  # 得到云端关注列表
        url_length = len(query_list)
        url_num = 0
        while True:
            if url_num < url_length:
                now_url = query_list[url_num].get('blogurl')
                first_spider = Get_First_Url(now_url)  # 获取主页的第一篇博客地址（可能不是最新发表的一篇）
                begin_url = first_spider.beginurl
                if (begin_url != 'nourl'):  # 如果存在url

                    print('获取列表成功，爬取第' + str(url_num) + '个')

                    spider = CSDN_Blog_Spider(begin_url, 4)  # 4代表初始化，第一次先判断有没有下一篇，如果有则记录，等爬完上一篇回来爬下一篇

                    while True:  # 爬取上一篇
                        next_url = spider.getNextArticle()
                        if next_url != None:
                            spider = CSDN_Blog_Spider(next_url, 3)
                        elif next_url is None:  # 没有上一篇，检查下一篇
                            print('开始爬取下一篇')
                            global WAIT_URL
                            if WAIT_URL != None:
                                spider = CSDN_Blog_Spider(WAIT_URL, 3)  # 3 代表下一篇
                                while True:  # 开始爬取下一篇
                                    next_url = spider.getLastArticleUrl()
                                    if next_url != None:
                                        spider = CSDN_Blog_Spider(next_url, 3)
                                    elif next_url is None:
                                        print('爬虫准备爬下一个地方啦')
                                        break

                                    print('休眠10s')
                                    time.sleep(10)
                                    print('休眠结束，继续爬取数据')

                            print('爬虫准备爬下一个地方啦')
                            break

                        print('休眠10s')
                        time.sleep(10)
                        print('休眠结束，继续爬取数据')

                    url_num = url_num + 1
            else:
                print('爬虫全部爬完了')
                break
                # 读取云端存储的关注列表 - -end


# leancloud初始化，请填入自己的id和key
leancloud.init('', '')

url = ""
Scheduler(url).start()
