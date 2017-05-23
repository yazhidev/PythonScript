# coding=utf-8

import xlrd
import xlwt
import os, sys
import datetime
import time

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
SOUGOU_NEW = u"新搜狗"
SEO_PC = u"seo_pc"
SEO_WAP = u"seo_wap"

REGISTER_TYPE = 0
MSG_TYPE = 1
CARD_TYPE = 2
SUM = 3  # 总和
DAY_OF_WEEK_ITEM_NUM = 7  # 分星期表每天的item数


# 判断手机/时间列数
# 分时按天
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
        self.warning = "\n"
        self.isReading = ""
        self.weekDataMapBaiduPc = {}  # 每周七天分时map，{0:{24个DayInWeekData...], },1:[]} 对应周日分时数据、周一分时数据
        self.weekDataMapBaiduWap = {}
        self.allDataMap = {}  # 列表存储每天的渠道列表  {"2017-04-08":[[注册的渠道],[留言的渠道],[名片的渠道],[总数]]、...}
        self.allSum = 0  # 所有线索总和
        self.items = [BAIDU_WAP, BAIDU_PC, BAIDU_WM, BAIDU_ZSYX, SOUGOU_WAP, SOUGOU_PC, QIHU360_WAP,
                      QIHU360_PC, SHENMA, ORTHER, SEO_PC, SEO_WAP, SOUGOU_NEW]

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
        global SOUGOU_NEW
        global SEO_PC
        global SEO_WAP
        global SUM
        global DAY_OF_WEEK_ITEM_NUM

        # 注册
        self.read_data(0, 5, REGISTER_TYPE)  # 参数是 时间是第几列、手机号在第几列、类型（0注册，1留言，2名片）
        # 留言
        self.read_data(2, 5, MSG_TYPE)
        # 名片
        self.read_data(12, 5, CARD_TYPE)
        # 绘制各渠道几个表线索总和
        self.writeSum()
        # 绘制每小时百度线索
        self.writeEveryHourBaiduData()
        # 消费表
        self.readComsumeData(True)
        self.readComsumeData(False)
        # 绘制分星期表
        self.writeConsumerData()

        if self.warning == "\n":
            print("数据文件生成成功！3秒后自动关闭程序 \n")
            time.sleep(3)
        else:
            print(self.warning)
            input("按回车键（Enter键））关闭程序 \n")

    # 将百度的数据添加到小时列表里
    def get_every_hour_data(self, isPc, time):
        nowHourTime = time[11: 13]
        if nowHourTime[0:1] == "0":
            hourIndex = int(nowHourTime[1:2])  # 获取小时列表的行号
        else:
            hourIndex = int(nowHourTime)

        dayOfWeek = self.getDayInWeek(time)

        if isPc == True:
            self.everyBaiduPCHourNumList[hourIndex] += 1

            ## 先判断是周几
            if dayOfWeek not in self.weekDataMapBaiduPc:
                # 还未存在则初始化
                thisDayData = []
                for i in range(24):  # 该天分时线索列表初始化
                    thisDayData.append(DayInWeekData())
                self.weekDataMapBaiduPc[dayOfWeek] = thisDayData

            # 添加线索到分星期消费表中
            self.weekDataMapBaiduPc[dayOfWeek][hourIndex].number += 1
        else:
            self.everyBaiduWAPHourNumList[hourIndex] += 1

            ## 先判断是周几
            if dayOfWeek not in self.weekDataMapBaiduWap:
                # 还未存在则初始化
                thisDayData = []
                for i in range(24):  # 该天分时线索列表初始化
                    thisDayData.append(DayInWeekData())
                self.weekDataMapBaiduWap[dayOfWeek] = thisDayData

            # 添加线索到分星期消费表中
            self.weekDataMapBaiduWap[dayOfWeek][hourIndex].number += 1

    def findExcel(self, name):
        data = 0
        num = 1;
        for fileName in os.listdir(sys.path[0]):
            if (fileName.find(name) != -1) and (fileName.find(".xls") != -1) and (
                    (fileName.find("~$") == -1)):
                if num > 1:
                    self.warning = self.warning + "警告！ 发现多个 " + name + " 文件 \n"
                else:
                    print("开始统计：", fileName)
                    self.isReading = fileName
                    data = xlrd.open_workbook(fileName)  # 读取excel文件
                    num += 1

        if data == 0:
            self.warning = self.warning + "警告！ 未发现 " + name + " 文件，是否忘记将 csv 转换格式为  xlsx ?\n"
        return data

    def read_data(self, timeIndex, phoneNumIndex, type):  # 参数是 时间是第几列、手机号在第几列、类型（0注册，1留言，2名片）

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
                continue
            self.phoneNumList.append(thisPhontNum)  # 添加手机号
            thisUrl = str(thisLine[len(thisLine) - 1])  # 获取最后一列数据，即网址
            time = str(thisLine[timeIndex]).strip()  # 时间
            nowDayTime = time[0: 10]

            if nowDayTime not in self.allDataMap:  # 还没有这一天的数据
                thisDayDataList = []  # 当天数据[[注册的渠道],[留言的渠道],[名片的渠道]
                for j in range(SUM + 1):  # 初始化当天三种来源列表
                    thisDayDataList.append([])
                self.allDataMap[nowDayTime] = thisDayDataList

            mj = self.getMj(thisUrl)
            thisUrl = thisUrl.strip()
            if thisUrl == "http://m.fudaojun.com/":  # SEO wap
                self.appendDataToAllDataMap(nowDayTime, type, SEO_WAP)
            elif thisUrl == "http://www.fudaojun.com/":  # SEO pc
                self.appendDataToAllDataMap(nowDayTime, type, SEO_PC)
            elif (thisUrl.find("shenma") != -1) or (mj != -1 and mj.find("sm") != -1):  # 神马
                self.appendDataToAllDataMap(nowDayTime, type, SHENMA)
            elif thisUrl.find("semwm") != -1:  # 百度网盟
                self.appendDataToAllDataMap(nowDayTime, type, BAIDU_WM)
            elif thisUrl.find("semzhishiyingxiao") != -1:  # 百度知识营销
                self.appendDataToAllDataMap(nowDayTime, type, BAIDU_ZSYX)
            elif thisUrl.find("http://fudaojun.yytsw.net.cn/") != -1:  # 新搜狗
                self.appendDataToAllDataMap(nowDayTime, type, SOUGOU_NEW)
            elif thisUrl.find("http://m.fudaojun.com/") != -1:  # wap端
                if (thisUrl.find("sogou") != -1) or (mj != -1 and mj.find("sg") != -1):  # 搜狗
                    self.appendDataToAllDataMap(nowDayTime, type, SOUGOU_WAP)
                elif thisUrl.find("360") != -1:  # 360
                    self.appendDataToAllDataMap(nowDayTime, type, QIHU360_WAP)
                elif len(thisUrl) > 0:  # 其他算百度
                    self.appendDataToAllDataMap(nowDayTime, type, BAIDU_WAP)
                    self.get_every_hour_data(False, time)

                else:  # 没有地址算其他
                    self.appendDataToAllDataMap(nowDayTime, type, ORTHER)
                    # 什么都没带属于百度
                    # 地址为空 属于其他
                    # semwm  百度网盟 不分PC WAP
                    # semzhishiyingxiao  百度知识营销

                    # 其他百度

            else:  # PC端
                if (thisUrl.find("sogou") != -1) or (mj != -1 and mj.find("sg") != -1):  # 搜狗
                    self.appendDataToAllDataMap(nowDayTime, type, SOUGOU_PC)
                elif thisUrl.find("360") != -1:  # 360
                    self.appendDataToAllDataMap(nowDayTime, type, QIHU360_PC)
                elif len(thisUrl) > 0:  # 其他算百度，没有地址算其他
                    self.appendDataToAllDataMap(nowDayTime, type, BAIDU_PC)
                    self.get_every_hour_data(True, time)
                else:
                    self.appendDataToAllDataMap(nowDayTime, type, ORTHER)

        self.write_excel(self.allDataMap, type)

    def appendDataToAllDataMap(self, dayTime, type, item):
        self.allDataMap[dayTime][type].append(item)
        self.allDataMap[dayTime][SUM].append(item)

    def getMj(self, thisUrl):
        mj = -1
        if thisUrl.find("&mj=") != -1:  # 截取mj的值
            mjStrNum = thisUrl.find("&mj=")
            zjStrNum = thisUrl.find("&zj=")
            if zjStrNum != -1:
                mj = thisUrl[mjStrNum + 4:zjStrNum]  # 切割&mj=  和  &zj= 之间的值
        return mj

    # 星期日是0
    def getDayInWeek(self, time):
        return datetime.datetime(int(time[0:4]), int(time[5:7]), int(time[8:10])).strftime("%w");

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
            sheet1.write_merge(0, 0, 2, 5, u"线索量", self.style)
            sheet1.write(1, 2, u"注册", self.style)
            sheet1.write(1, 3, u"留言", self.style)
            sheet1.write(1, 4, u"名片", self.style)
            sheet1.write(1, 5, u"总计", self.style)

        else:
            sheet1 = self.excel.get_sheet(u"每天各渠道线索")

        beginRow = 2  # 本日期开始写数据的行号
        dataLine = 2 + type  # 写入数据的列号

        for keyOfDay in allDataMap:  # 遍历map里所有的时间
            thisList = allDataMap[keyOfDay]
            if self.isWriteSheet1 == False:
                sheet1.write_merge(beginRow, beginRow + len(self.items), 0, 0, keyOfDay, self.style)

            num = 0
            for i in range(len(self.items)):  # 遍历一天内所有的渠道的线索数量
                if self.isWriteSheet1 == False:
                    sheet1.write(beginRow + i, 1, self.items[i], self.style)  # 写渠道名
                    if i == 0:
                        sheet1.write(beginRow + len(self.items), 1, u"总计", self.style)  # 总和
                thisItemNum = thisList[type].count(self.items[i])  # 某个渠线索道数量
                sheet1.write(beginRow + i, dataLine, thisItemNum, self.style)  # 写线索数
                num += thisItemNum
                # 读取该渠道总和列的数值，加上这个表的总和

            # 这个表的线索总和
            self.allSum += num
            sheet1.write(beginRow + len(self.items), dataLine, num, self.style)

            beginRow = beginRow + len(self.items) + 1

        self.excel.save(u'数据.xls')
        self.isWriteSheet1 = True

    # 写各渠道几个表的线索总和
    def writeSum(self):
        sheet1 = self.excel.get_sheet(u"每天各渠道线索")
        beginRow = 2  # 本日期开始写数据的行号
        dataLine = 2 + SUM  # 写入数据的列号

        for keyOfDay in self.allDataMap:  # 遍历map里所有的时间
            thisList = self.allDataMap[keyOfDay]
            for i in range(len(self.items)):  # 遍历一天内所有的渠道的线索数量
                thisItemSum = thisList[SUM].count(self.items[i])  # 某个渠线索道数量
                sheet1.write(beginRow + i, dataLine, thisItemSum, self.style)  # 写线索数
                # 读取该渠道总和列的数值，加上这个表的总和

            sheet1.write(beginRow + len(self.items), dataLine, self.allSum, self.style)

            beginRow = beginRow + len(self.items) + 1

        self.excel.save(u'数据.xls')

    # 读取消费账号
    # zhanghupc 代表PC zhanghuwap
    def readComsumeData(self, isPc):
        if isPc == True:
            data = self.findExcel("zhanghupc")
        else:
            data = self.findExcel("zhanghuwap")

        if data == 0:
            return

        table = data.sheets()[0]  # 第一张表
        fileRows = table.nrows  # 行数

        for i in range(8, fileRows):  # 从第二行开始，遍历24小时
            thisLine = table.row_values(i)  # 获取一整行数据
            data = xlrd.xldate_as_tuple(thisLine[0], 0)
            strM = "-"
            if (data[1] < 10):
                strM += "0" + str(data[1])
            else:
                strM += str(data[1])
            strD = "-"
            if (data[2] < 10):
                strD += "0" + str(data[2])
            else:
                strD += str(data[2])

            dayStr = str(data[0]) + strM + strD
            dayOfWeek = self.getDayInWeek(dayStr)
            ## 先判断是周几
            if isPc == True:
                map = self.weekDataMapBaiduPc
            else:
                map = self.weekDataMapBaiduWap

            if dayOfWeek not in map:
                # 还未存在则初始化
                thisDayData = []
                for j in range(24):  # 该天分时线索列表初始化
                    thisDayData.append(DayInWeekData())
                map[dayOfWeek] = thisDayData

            if isPc == True:
                if str(thisLine[2]) != "hz微著": # 简单判断文件内容是否有误
                    self.warning = self.warning + "警告！ zhanghuPC 文件内第 " + str(
                        i) + " 行发现 非'hz微著' 标识，请检查文件是否正确 \n"
                    return

            if isPc == False:
                if str(thisLine[2]) != "微著网络":
                    self.warning = self.warning + "警告！ zhanghuWAP 文件内第 " + str(
                        i) + " 行发现 非'微著网络' 标识，请检查文件是否正确 \n"
                    return

            newHourInt = int(str(thisLine[1]).replace(".0", ""))  # 小时
            thisDayData = map[dayOfWeek][newHourInt]  # 当天数据，例如周一的数据
            thisDayData.show += int(str(thisLine[3]).replace(".0", ""))  # 展现
            thisDayData.click += int(str(thisLine[4]).replace(".0", ""))  # 点击
            thisDayData.comsumer += float(thisLine[5])  # 消费

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

        self.excel.save(u'数据.xls')

    def writeConsumerData(self):
        sheet3 = self.excel.add_sheet(u"百度分星期表")

        # 绘制表头
        sheet3.write_merge(0, 1, 0, 0, u"渠道", self.style)
        sheet3.write_merge(0, 1, 1, 1, u"时间", self.style)
        sheet3.write_merge(2, 25, 0, 0, u"百度PC", self.style)
        sheet3.write_merge(26, 49, 0, 0, u"百度WAP", self.style)

        drawPcTime = False
        drawWapTime = False

        dayOfWeekStr = [u"周日", u"周一", u"周二", u"周三", u"周四", u"周五", u"周六"]

        dayBeginX = 2  # 周日开始的x轴数值
        for i in range(7):  # 遍历0~6
            sheet3.write_merge(0, 0, dayBeginX, dayBeginX + DAY_OF_WEEK_ITEM_NUM - 1,
                               dayOfWeekStr[i],
                               self.style)
            sheet3.write(1, dayBeginX, u"消费", self.style)
            sheet3.write(1, dayBeginX + 1, u"展现", self.style)
            sheet3.write(1, dayBeginX + 2, u"点击", self.style)
            sheet3.write(1, dayBeginX + 3, u"点击率", self.style)
            sheet3.write(1, dayBeginX + 4, u"平均点击价格", self.style)
            sheet3.write(1, dayBeginX + 5, u"线索量", self.style)
            sheet3.write(1, dayBeginX + 6, u"线索成本", self.style)
            firstCol = sheet3.col(dayBeginX + 4)
            firstCol.width = 256 * 12  # 平均点击价格列宽度设大一点

            pcBeginY = 2
            if str(i) in self.weekDataMapBaiduPc:  # 如果有当天数据，写入excel
                for hour in range(24):  # 遍历24小时
                    if drawPcTime == False:  # 绘制PC小时
                        sheet3.write(pcBeginY + hour, 1, str(hour) + u" 时", self.style)
                    thisHourData = self.weekDataMapBaiduPc[str(i)][hour]
                    self.writeData(sheet3, dayBeginX, pcBeginY, hour, thisHourData)
                drawPcTime = True

            pcBeginY += 24
            if str(i) in self.weekDataMapBaiduWap:  # 如果有当天数据，写入excel
                for hour in range(24):  # 遍历24小时
                    if drawWapTime == False:  # 绘制PC小时
                        sheet3.write(pcBeginY + hour, 1, str(hour) + u" 时", self.style)
                    thisHourData = self.weekDataMapBaiduWap[str(i)][hour]
                    self.writeData(sheet3, dayBeginX, pcBeginY, hour, thisHourData)
                drawWapTime = True

            dayBeginX += DAY_OF_WEEK_ITEM_NUM

        self.excel.save(u'数据.xls')

    def writeData(self, sheet, dayBeginX, pcBeginY, hour, thisHourData):
        sheet.write(pcBeginY + hour, dayBeginX, thisHourData.comsumer,
                    self.style)  # 消费
        sheet.write(pcBeginY + hour, dayBeginX + 1, thisHourData.show,
                    self.style)  # 展现
        sheet.write(pcBeginY + hour, dayBeginX + 2, thisHourData.click,
                    self.style)  # 点击
        sheet.write(pcBeginY + hour, dayBeginX + 3,
                    thisHourData.show if thisHourData.show == 0 else '%.2f%%' % (round(
                        thisHourData.click / thisHourData.show, 4) * 100),
                    self.style)  # 点击率
        sheet.write(pcBeginY + hour, dayBeginX + 4,
                    thisHourData.click if thisHourData.click == 0 else round(
                        thisHourData.comsumer / thisHourData.click, 2),
                    self.style)  # 平均点击价格
        sheet.write(pcBeginY + hour, dayBeginX + 5, thisHourData.number,
                    self.style)  # 线索量
        sheet.write(pcBeginY + hour, dayBeginX + 6,
                    -thisHourData.comsumer if thisHourData.number == 0 else round(
                        thisHourData.comsumer / thisHourData.number, 2),
                    self.style)  # 线索成本


# 每周七天分时数据模型
class DayInWeekData:
    def __init__(self):
        self.show = 0  # 展现
        self.click = 0  # 点击
        self.comsumer = 0  # 消费
        self.number = 0  # 线索量
        self.price = 0  # 线索成本=消费/线索量
        self.clickPercent = 0  # 点击率=点击/展现
        self.averageClickPrice = 0  # 平均点击价格=消费/点击
        # 新增项目是要去更改项目的数量 DAY_OF_WEEK_ITEM_NUM


# 运行
readData = ReadData()
try:
    readData.start()
except Exception as e:
    if str(e).find("Permission denied: '数据.xls") != -1:
        print("警告！ 保存数据错误，请关闭  数据.xls  文件后重试 \n")
        input("按回车键（Enter键））关闭程序 \n")
    else:
        print("警告！ 请检查", readData.isReading, "文件格式、内容是否有误，如果文件没有问题请联系小帅修复程序 \n")
        input("按回车键（Enter键））关闭程序 \n")

# pip install pyexcel-xls 安装模块
