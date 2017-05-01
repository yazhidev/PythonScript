# coding=utf-8

import xlrd
import xlwt
import os, sys

SHENMA = u"神马"
BAIDU_PC = u"百度pc"
BAIDU_WAP = u"百度wap"
SOUGOU_PC = u"搜狗pc"
SOUGOU_WAP = u"搜狗wap"
QIHU360_PC = u"360_pc"
QIHU360_WAP = u"360_wap"
BAIDU_WM = u"百度网盟"
BAIDU_ZSYX = u"百度知识营销"
ORTHER = u"其他"

REGISTER_TYPE = 0
MSG_TYPE = 1
CARD_TYPE = 2


class ReadData:
    def __init__(self):
        self.phoneNumList = []  # 记录手机号，用于手机去重的列表
        self.excel = xlwt.Workbook()  # 生成excel表
        self.style = xlwt.XFStyle()
        alignment = xlwt.Alignment()  # 居中对齐
        alignment.horz = xlwt.Alignment.HORZ_CENTER
        alignment.vert = xlwt.Alignment.VERT_CENTER
        self.style.alignment = alignment
        self.everyBaiduWAPHourNumList = []  # 记录百度WAP每个小时的数量的列表
        self.everyBaiduPCHourNumList = []  # 记录百度PC每个小时的数量的列表
        self.isWriteSheet1 = False
        for i in range(24):  # 分时线索列表初始化
            self.everyBaiduWAPHourNumList.append(0)
            self.everyBaiduPCHourNumList.append(0)

    def start(self):
        global REGISTER_TYPE
        global MSG_TYPE
        global CARD_TYPE
        global BAIDU_WAP
        global SHENMA
        global SOUGOU_PC
        global SOUGOU_WAP
        global QIHU360_WAP
        global BAIDU_WAP
        global QIHU360_PC
        global BAIDU_WM
        global BAIDU_ZSYX
        global ORTHER

        # 注册
        self.read_data(0, 5, REGISTER_TYPE)  # 参数是 时间在第几列、类型（0注册，1留言，2名片）
        # 留言
        self.read_data(2, 5, MSG_TYPE)
        # 名片
        self.read_data(12, 5, CARD_TYPE)
        # 绘制每小时百度线索
        self.writeEveryHourBaiduData()

    # 将百度的数据添加到小时列表里
    def get_every_hour_data(self, isPc, time):
        nowHourTime = time[12: 14]
        if nowHourTime[0:1] == "0":
            hourIndex = int(nowHourTime[1:2])  # 获取小时列表的行号
        else:
            hourIndex = int(nowHourTime)

        if isPc == True:
            self.everyBaiduPCHourNumList[hourIndex] += 1
        else:
            self.everyBaiduWAPHourNumList[hourIndex] += 1

    def findExcel(self, name):
        data = 0
        for fileName in os.listdir(sys.path[0]):
            if fileName.find(name) != -1:
                print fileName
                data = xlrd.open_workbook(fileName)  # 读取excel文件
                break

        if data == 0:
            print "未发现 ", name, " 文件"
        return data

    def read_data(self, timeIndex, phoneNumIndex, type):  # 参数是 时间是第几列、手机号在第几列、类型（0注册，1留言，2名片）
        allDataMap = {}  # 列表存储每天的渠道列表  {"2017-04-08":[[注册的渠道],[留言的渠道],[名片的渠道]]、...}

        data = 0
        if type == REGISTER_TYPE:
            data = self.findExcel("注册数据")
            if data == 0:
                return
        elif type == MSG_TYPE:
            data = self.findExcel("访客留言")
            if data == 0:
                return
        elif type == CARD_TYPE:
            data = self.findExcel("访客名片")
            if data == 0:
                return
        else:
            return

        table = data.sheets()[0]  # 第一张表
        fileRows = table.nrows  # 行数

        for i in range(1, fileRows):  # 从第二行开始
            thisLine = table.row_values(i)  # 获取一整行数据
            thisPhontNum = str(thisLine[phoneNumIndex])
            if thisPhontNum in self.phoneNumList:  # 重复手机号，去重，忽略本条
                print "第 ", i + 1, " 行 手机号去重 号码:", thisPhontNum
                continue
            self.phoneNumList.append(thisPhontNum)  # 添加手机号
            thisUrl = str(thisLine[len(thisLine) - 1])  # 获取最后一列数据，即网址
            time = str(thisLine[timeIndex])  # 时间
            nowDayTime = time[0: 12]
            nowDayTime = nowDayTime.lstrip()

            if allDataMap.has_key(nowDayTime) == False:  # 还没有这一天的数据
                thisDayDataList = []  # 当天数据[[注册的渠道],[留言的渠道],[名片的渠道]
                for j in range(3):  # 初始化当天三种来源列表
                    thisDayDataList.append([])
                allDataMap[nowDayTime] = thisDayDataList

            mj = self.getMj(thisUrl)
            if (thisUrl.find("shenma") != -1) or (mj != -1 and mj.find("sm") != -1):  # 神马
                allDataMap[nowDayTime][type].append(SHENMA)
                print "第 ", i + 1, " 行 神马 ", thisUrl
            elif thisUrl.find("semwm") != -1:  # 百度网盟
                allDataMap[nowDayTime][type].append(BAIDU_WM)
            elif thisUrl.find("semzhishiyingxiao") != -1:  # 百度知识营销
                allDataMap[nowDayTime][type].append(BAIDU_ZSYX)
            elif thisUrl.find("http://m.fudaojun.com/") != -1:  # wap端
                if (thisUrl.find("sogou") != -1) or (mj != -1 and mj.find("sg") != -1):  # 搜狗
                    print "第 ", i + 1, " 行 搜狗wap", thisUrl
                    allDataMap[nowDayTime][type].append(SOUGOU_WAP)
                elif thisUrl.find("360") != -1:  # 360
                    print "第 ", i + 1, " 行 360wap", thisUrl
                    allDataMap[nowDayTime][type].append(QIHU360_WAP)
                elif len(thisUrl) > 0:  # 其他算百度
                    print "第 ", i + 1, " 行 百度wap ", thisUrl
                    allDataMap[nowDayTime][type].append(BAIDU_WAP)
                    self.get_every_hour_data(False, time)
                else: #没有地址算其他
                    print "第 ", i + 1, " 行 wap 其他 ", thisUrl.strip(), "--", len(thisUrl)
                    allDataMap[nowDayTime][type].append(ORTHER)
                    # 什么都没带属于百度
                    # 地址为空 属于其他
                    # semwm  百度网盟 不分PC WAP
                    # semzhishiyingxiao  百度知识营销

                    # 其他百度


            else:  # PC端
                if (thisUrl.find("sogou") != -1) or (mj != -1 and mj.find("sg") != -1):  # 搜狗
                    print "第 ", i + 1, " 行 搜狗pc", thisUrl
                    allDataMap[nowDayTime][type].append(SOUGOU_PC)
                elif thisUrl.find("360") != -1:  # 360
                    print "第 ", i + 1, " 行 360pc", thisUrl
                    allDataMap[nowDayTime][type].append(QIHU360_PC)
                elif len(thisUrl) > 0:  # 其他算百度，没有地址算其他
                    print "第 ", i + 1, " 行 百度pc ", thisUrl
                    allDataMap[nowDayTime][type].append(BAIDU_PC)
                    self.get_every_hour_data(True, time)
                else:
                    print "第 ", i + 1, " 行 wap 其他 ", thisUrl.strip()
                    allDataMap[nowDayTime][type].append(ORTHER)

        self.write_excel(allDataMap, type)

    def getMj(self, thisUrl):
        mj = -1
        if thisUrl.find("&mj=") != -1:  # 截取mj的值
            mjStrNum = thisUrl.find("&mj=")
            zjStrNum = thisUrl.find("&zj=")
            if zjStrNum != -1:
                mj = thisUrl[mjStrNum + 4:zjStrNum]  # 切割&mj=  和  &zj= 之间的值
        return mj

    # 写入当前读取到时间与各渠道数量
    def write_excel(self, allDataMap, type):
        if self.isWriteSheet1 == False:
            sheet1 = self.excel.add_sheet(u"每天各渠道线索")
            # 绘制表头
            sheet1.write_merge(0, 1, 0, 0, u"日期", self.style)
            firstCol = sheet1.col(0)
            secondCol = sheet1.col(1)
            firstCol.width = 256 * 15  # 时间列宽度设大一点
            secondCol.width = 256 * 12  # 渠道名称列宽度设大一点
            sheet1.write_merge(0, 1, 1, 1, u"渠道", self.style)
            sheet1.write_merge(0, 0, 2, 4, u"线索量", self.style)
            sheet1.write(1, 2, u"注册", self.style)
            sheet1.write(1, 3, u"留言", self.style)
            sheet1.write(1, 4, u"名片", self.style)

        else:
            sheet1 = self.excel.get_sheet(u"每天各渠道线索")

        beginRow = 2  # 本日期开始写数据的行号
        dataLine = 2 + type  # 写入数据的列号

        items = [BAIDU_WAP, BAIDU_PC, BAIDU_WM, BAIDU_ZSYX, SOUGOU_WAP, SOUGOU_PC, QIHU360_WAP,
                 QIHU360_PC, SHENMA, ORTHER]
        for key in allDataMap:
            thisList = allDataMap[key]
            if self.isWriteSheet1 == False:
                sheet1.write_merge(beginRow, beginRow + len(items) - 1, 0, 0, key, self.style)

            for i in range(len(items)):
                if self.isWriteSheet1 == False:
                    sheet1.write(beginRow + i, 1, items[i], self.style)  # 写渠道名
                sheet1.write(beginRow + i, dataLine, thisList[type].count(items[i]),
                             self.style)  # 写线索数

            beginRow = beginRow + len(items)

        self.excel.save('myTest.xlsx')
        self.isWriteSheet1 = True

    # 写入百度分时线索量
    def writeEveryHourBaiduData(self):
        sheet2 = self.excel.add_sheet(u"百度分时段线索")
        # 绘制表头
        sheet2.write(0, 0, u"渠道", self.style)
        sheet2.write(0, 1, u"时段", self.style)
        sheet2.write(0, 2, u"线索量", self.style)
        sheet2.write(0, 4, u"渠道", self.style)
        sheet2.write(0, 5, u"时段", self.style)
        sheet2.write(0, 6, u"线索量", self.style)
        sheet2.write_merge(1, 24, 0, 0, u"百度PC", self.style)
        sheet2.write_merge(1, 24, 4, 4, u"百度WAP", self.style)

        for i in range(len(self.everyBaiduPCHourNumList)):
            sheet2.write(1 + i, 1, str(i) + u" 时", self.style)
            sheet2.write(1 + i, 2, self.everyBaiduPCHourNumList[i], self.style)
            sheet2.write(1 + i, 5, str(i) + u" 时", self.style)
            sheet2.write(1 + i, 6, self.everyBaiduWAPHourNumList[i], self.style)

        self.excel.save('myTest.xlsx')


# 运行
ReadData().start()

# pip install pyexcel-xls 安装模块
