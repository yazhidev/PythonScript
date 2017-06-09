# coding=utf-8

import xlrd
import xlwt
import os, sys
import datetime
import time

REGISTER_TYPE = 0
MSG_TYPE = 1
CARD_TYPE = 2
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
        self.isWriteSheet1 = False
        self.warning = "\n"
        self.isReading = ""
        self.allDataMap = {}  # 列表存储每天的渠道列表  {"2017-04-08": DayData、...}
        self.weekDataMapBaiduPc = {}  # 每周七天分时map，{0:{24个DayInWeekData...], },1:[]} 对应周日分时数据、周一分时数据
        self.weekDataMapBaiduWap = {}
        self.dataDetailList = []

    def start(self):
        global REGISTER_TYPE
        global MSG_TYPE
        global CARD_TYPE
        global DAY_OF_WEEK_ITEM_NUM

        # 读取注册表
        self.read_data(0, 5, REGISTER_TYPE)  # 参数是 时间是第几列、手机号在第几列、类型（0注册，1留言，2名片）
        # 读取留言表
        self.read_data(2, 5, MSG_TYPE)
        # 读取名片表
        self.read_data(12, 5, CARD_TYPE)
        # 绘制各渠道线索表
        self.writeChannelData()
        # 绘制每小时百度线索
        self.writeEveryHourBaiduData()
        # 读取账户消费表
        self.readComsumeData(True)
        self.readComsumeData(False)
        # 绘制分星期表
        self.writeConsumerData()
        # 绘制线索信息表
        self.writeDataDetail()

        if self.warning == "\n":
            print("数据文件生成成功！3秒后自动关闭程序 \n")
            time.sleep(3)
        else:
            print(self.warning)
            input("按回车键（Enter键））关闭程序 \n")

    # 将百度的数据添加到小时列表里
    def get_every_hour_data(self, isPc, time, data):
        nowHourTime = time[11: 13]
        if nowHourTime[0:1] == "0":
            hourIndex = int(nowHourTime[1:2])  # 获取小时列表的行号
        else:
            hourIndex = int(nowHourTime)

        data[hourIndex] += 1

        # 添加分星期数据
        dayOfWeek = self.getDayInWeek(time)
        if isPc == True:
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

            # 添加线索数据，并设置数据
            thisData = DataDetail(type)
            thisData.setData(thisLine)

            thisUrl = str(thisLine[len(thisLine) - 1])  # 获取最后一列数据，即网址
            time = str(thisLine[timeIndex]).strip()  # 时间
            nowDayTime = time[0: 10]

            if nowDayTime not in self.allDataMap:  # 还没有这一天的数据
                self.allDataMap[nowDayTime] = DayData()

            mj = self.getMj(thisUrl)
            thisUrl = thisUrl.strip()
            thisDayData = self.allDataMap[nowDayTime]
            thisDayData.all.addNum(type)
            if thisUrl == "http://m.fudaojun.com/":  # SEO wap
                thisDayData.seowap.addNum(type)
                thisData.channel = thisDayData.seowap.name
            elif thisUrl == "http://www.fudaojun.com/":  # SEO pc
                thisDayData.seopc.addNum(type)
                thisData.channel = thisDayData.seopc.name
            elif thisUrl.find("http://fudaojun.dayijun.com/") != -1:  # 神马2
                thisDayData.shenma2.addNum(type)
                thisData.channel = thisDayData.shenma2.name
            elif (thisUrl.find("shenma") != -1) or (mj != -1 and mj.find("sm") != -1):  # 神马
                thisDayData.shenma.addNum(type)
                thisData.channel = thisDayData.shenma.name
            elif thisUrl.find("semwm") != -1:  # 百度网盟
                thisDayData.baiduwm.addNum(type)
                thisData.channel = thisDayData.baiduwm.name
            elif thisUrl.find("semzhishiyingxiao") != -1:  # 百度知识营销
                thisDayData.baiduzs.addNum(type)
                thisData.channel = thisDayData.baiduzs.name
            elif thisUrl.find("http://fudaojun.yytsw.net.cn/") != -1:  # 新搜狗
                thisDayData.sogouNew.addNum(type)
                thisData.channel = thisDayData.sogouNew.name
            elif thisUrl.find("http://m.fudaojun.com/") != -1:  # wap端
                if (thisUrl.find("sogou") != -1) or (mj != -1 and mj.find("sg") != -1):  # 搜狗
                    thisDayData.sogouwap.addNum(type)
                    thisData.channel = thisDayData.sogouwap.name
                elif thisUrl.find("360") != -1:  # 360
                    thisDayData.wap360.addNum(type)
                    thisData.channel = thisDayData.wap360.name
                elif len(thisUrl) > 0:  # 其他算百度
                    thisDayData.baiduwap.addNum(type)
                    thisData.channel = thisDayData.baiduwap.name
                    self.get_every_hour_data(False, time, thisDayData.baiduwap.hourNumList)

                else:  # 没有地址算其他
                    thisDayData.other.addNum(type)
                    thisData.channel = thisDayData.other.name
                    # 什么都没带属于百度
                    # 地址为空 属于其他
                    # semwm  百度网盟 不分PC WAP
                    # semzhishiyingxiao  百度知识营销
                    # 其他百度

            else:  # PC端
                if (thisUrl.find("sogou") != -1) or (mj != -1 and mj.find("sg") != -1):  # 搜狗
                    thisDayData.sogoupc.addNum(type)
                    thisData.channel = thisDayData.sogoupc.name
                elif thisUrl.find("360") != -1:  # 360
                    thisDayData.pc360.addNum(type)
                    thisData.channel = thisDayData.pc360.name
                elif len(thisUrl) > 0:  # 其他算百度，没有地址算其他
                    thisDayData.baidupc.addNum(type)
                    thisData.channel = thisDayData.baidupc.name
                    self.get_every_hour_data(True, time, thisDayData.baidupc.hourNumList)
                else:
                    thisDayData.other.addNum(type)
                    thisData.channel = thisDayData.other.name

            self.dataDetailList.append(thisData)

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
    def writeChannelData(self):
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

        for keyOfDay in self.allDataMap:  # 遍历map里所有的时间
            thisDayData = self.allDataMap[keyOfDay]
            i = 0
            if thisDayData.isWriteTime == False:
                sheet1.write_merge(beginRow, beginRow + thisDayData.itemNum - 1, 0, 0, keyOfDay,
                                   self.style)  # 写时间
                thisDayData.isWriteTime = True
            for name, value in vars(thisDayData).items():  # 遍历当天数据的所有渠道
                if (name == "itemNum") or (name == "isWriteTime"):
                    continue
                if value.isWriteName == False:
                    sheet1.write(beginRow + i, 1, value.name, self.style)  # 写渠道名
                    value.isWriteName = True
                sheet1.write(beginRow + i, 2, value.register, self.style)  # 注册
                sheet1.write(beginRow + i, 3, value.msg, self.style)  # 留言
                sheet1.write(beginRow + i, 4, value.card, self.style)  # 名片
                sheet1.write(beginRow + i, 5, value.all, self.style)  # 总计
                i += 1

            beginRow = beginRow + thisDayData.itemNum

        self.excel.save(u'数据.xls')
        self.isWriteSheet1 = True

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
                if str(thisLine[2]) != "hz微著":  # 简单判断文件内容是否有误
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
        sheet2.write(0, 0, u"时间", self.style)
        firstCol = sheet2.col(0)
        firstCol.width = 256 * 15  # 时间列宽度设大一点
        sheet2.write(0, 1, u"渠道", self.style)
        sheet2.write(0, 2, u"时段", self.style)
        sheet2.write(0, 3, u"线索量", self.style)
        sheet2.write(0, 4, u"渠道", self.style)
        sheet2.write(0, 5, u"时段", self.style)
        sheet2.write(0, 6, u"线索量", self.style)

        beginY = 1

        for keyOfDay in self.allDataMap:  # 遍历map里所有的时间
            thisDayData = self.allDataMap[keyOfDay]
            if thisDayData.isWriteTime == True:
                sheet2.write_merge(beginY, beginY + 23, 0, 0, keyOfDay,
                                   self.style)  # 写时间
                thisDayData.isWriteTime = False

            sheet2.write_merge(beginY, beginY + 23, 1, 1, u"百度PC", self.style)
            sheet2.write_merge(beginY, beginY + 23, 4, 4, u"百度WAP", self.style)

            for i in range(len(thisDayData.baiduwap.hourNumList)):
                # 绘制百度pc分时
                sheet2.write(beginY + i, 2, str(i) + u" 时", self.style)
                sheet2.write(beginY + i, 3, thisDayData.baidupc.hourNumList[i], self.style)
                # 绘制百度wap分时
                sheet2.write(beginY + i, 5, str(i) + u" 时", self.style)
                sheet2.write(beginY + i, 6, thisDayData.baiduwap.hourNumList[i], self.style)

            beginY += 24

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

    def writeDataDetail(self):
        sheet4 = self.excel.add_sheet(u"线索数据表")

        # 绘制表头
        sheet4.write(0, 0, u"渠道", self.style)
        sheet4.write(0, 1, u"来源", self.style)
        sheet4.write(0, 2, u"创建时间", self.style)
        sheet4.write(0, 3, u"姓名", self.style)
        sheet4.write(0, 4, u"手机", self.style)
        sheet4.write(0, 5, u"访客地区", self.style)
        sheet4.write(0, 6, u"搜索词", self.style)
        sheet4.write(0, 7, u"最初访问", self.style)

        col1 = sheet4.col(2)
        col1.width = 256 * 19
        col2 = sheet4.col(4)
        col2.width = 256 * 15
        col3 = sheet4.col(5)
        col3.width = 256 * 16
        col4 = sheet4.col(6)
        col4.width = 256 * 19
        col5 = sheet4.col(7)
        col5.width = 256 * 19

        for index,value in enumerate(self.dataDetailList):
            sheet4.write(index + 1, 0, value.channel)
            sheet4.write(index + 1, 1, value.type, self.style)
            sheet4.write(index + 1, 2, value.time, self.style)
            sheet4.write(index + 1, 3, value.userName)
            sheet4.write(index + 1, 4, value.userPhone, self.style)
            sheet4.write(index + 1, 5, value.location)
            sheet4.write(index + 1, 6, value.keyWord)
            sheet4.write(index + 1, 7, value.firstUrl)

        self.excel.save(u'数据.xls')

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


# 每天的数据
class DayData:
    def __init__(self):
        self.itemNum = 15  # 总渠道数
        self.isWriteTime = False  # 是否绘制过时间
        self.baiduwap = ChannelData(u"百度wap")
        self.baiduwap.initHourData()
        self.baidupc = ChannelData(u"百度PC")
        self.baidupc.initHourData()
        self.baiduwm = ChannelData(u"百度网盟")
        self.baiduzs = ChannelData(u"百度知识营销")
        self.sogouwap = ChannelData(u"搜狗wap")
        self.sogoupc = ChannelData(u"搜狗pc")
        self.wap360 = ChannelData(u"360wap")
        self.pc360 = ChannelData(u"360pc")
        self.shenma = ChannelData(u"神马")
        self.other = ChannelData(u"其他")
        self.seopc = ChannelData(u"seo_pc")
        self.seowap = ChannelData(u"seo_wap")
        self.sogouNew = ChannelData(u"新搜狗")
        self.shenma2 = ChannelData(u"神马2")
        self.all = ChannelData(u"总计")

# 渠道数据
class ChannelData:
    def __init__(self, name):
        self.name = name
        self.register = 0  # 注册
        self.msg = 0  # 留言
        self.card = 0  # 名片
        self.all = 0  # 总计
        self.hourNumList = []  # 分时数据 hourNumList[3]的值代表3时的线索量
        self.isWriteName = False  # 是否绘制过渠道名

    def initHourData(self):
        # 初始化分时数据
        for i in range(24):
            self.hourNumList.append(0)

    def addNum(self, type):  # 对应渠道数量+1
        if type == REGISTER_TYPE:
            self.register += 1
            self.all += 1
        elif type == MSG_TYPE:
            self.msg += 1
            self.all += 1
        elif type == CARD_TYPE:
            self.card += 1
            self.all += 1
        else:
            return

# 线索数据表
class DataDetail:
    def __init__(self, type):
        self.channel = ""
        self.type = type
        self.time = ""
        self.userName = ""
        self.userPhone = ""
        self.location = ""
        self.keyWord = ""
        self.firstUrl = ""

    def setData(self, data):
        indexs = []
        if self.type == REGISTER_TYPE:
            self.type = u"注册" # 注册/留言/名片
            indexs = [0, 2, 5, 10, 12, len(data) - 1]
        elif self.type == MSG_TYPE:
            self.type = u"留言" # 注册/留言/名片
            indexs = [2, 4, 5, 15, 18, len(data) - 1]
        elif self.type == CARD_TYPE:
            self.type = u"名片" # 注册/留言/名片
            indexs = [12, 0, 5, 18, 21, len(data) - 1]

        time = str(data[indexs[0]]).strip()
        if time[len(time)-2:] == ".0":
            time = time[:len(time)-2]
        self.time = time  # 获取时间
        self.userName = str(data[indexs[1]]).strip()  # 获取用户名
        phone = str(data[indexs[2]]).strip()
        if phone[len(phone)-2:] == ".0":
            phone = phone[:len(phone)-2]
        self.userPhone = phone  # 获取手机
        self.location = str(data[indexs[3]]).strip()  # 获取地点
        self.keyWord = str(data[indexs[4]]).strip()  # 获取关键词
        self.firstUrl = str(data[indexs[5]]).strip()  # 获取地址



# 运行
readData = ReadData()
readData.start()
# try:
# except Exception as e:
#     if str(e).find("Permission denied: '数据.xls") != -1:
#         print("警告！ 保存数据错误，请关闭  数据.xls  文件后重试 \n")
#         input("按回车键（Enter键））关闭程序 \n")
#     else:
#         print("警告！ 请检查", readData.isReading, "文件格式、内容是否有误，如果文件没有问题请联系小帅修复程序 \n")
#         input("按回车键（Enter键））关闭程序 \n")

# pip install pyexcel-xls 安装模块
