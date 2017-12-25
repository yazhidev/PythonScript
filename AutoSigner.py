# coding=utf-8

import time
import os

class AutoEnterRoom:
    def __init__(self):
        self.waitTime = 10
        self.phoneType = 1
        self.enterRoomX = 0
        self.enterRoomY = 0
        self.quitRoomX = 0
        self.quitRoomY = 0
        self.isStudent = True

    def start(self):
        dataSize = input("课程数据量是否很大？默认是(y/n) \n")
        if (dataSize == "y") or (len(dataSize) == 0) :
            print("当前课程数据量较大")
            self.waitTime = 10
        elif dataSize == "n":
            print("当前课程数据量较小")
            self.waitTime = 5
        else:
            print("输入错误")
            return


        testPhone = input("选择机型：1（华为M2平板），2（小米平板2），3（Nexus5），4（红米2A），5（红米），6（vivo）默认1 \n")
        if (testPhone == "1") or (len(testPhone) == 0):
            print("当前机型：华为M2")
            self.enterRoomX = 400
            self.enterRoomY = 500
            self.quitRoomX = 1300
            self.quitRoomY = 610
            self.waitTime += 15
        elif testPhone == "2":
            print("当前机型：小米平板2")
            self.enterRoomX = 400
            self.enterRoomY = 640
            self.quitRoomX = 1480
            self.quitRoomY = 820
            self.waitTime += 3
        elif testPhone == "3":
            print("当前机型：Nexus5")
            self.enterRoomX = 200
            self.enterRoomY = 900
            self.quitRoomX = 1200
            self.quitRoomY = 610
            self.waitTime += 5
        elif testPhone == "4":
            print("当前机型：红米2A")
            self.enterRoomX = 200
            self.enterRoomY = 600
            self.quitRoomX = 1000
            self.quitRoomY = 410
            self.waitTime += 2
        elif testPhone == "5":
            print("当前机型：红米")
            self.enterRoomX = 150
            self.enterRoomY = 600
            self.quitRoomX = 1000
            self.quitRoomY = 410
            self.waitTime += 2
        elif testPhone == "6": 
            print("当前机型：vivo")
            self.enterRoomX = 150
            self.enterRoomY = 600
            self.quitRoomX = 1000
            self.quitRoomY = 410
            self.waitTime += 2
        else:
            print("不存在该机型")
            return

        isStudent = input("是否测试学生端进入教室？默认是(y/n) \n")
        if (isStudent == "y") or (len(isStudent) == 0):
            self.isStudent = True
            print("即将测试学生端")
        elif isStudent == "n":
            self.isStudent = False
            print("即将测试旁听端")
        else:
            print("输入错误，默认设为学生端")
            self.isStudent = True

        print("开始自动化进出教室") #程序奔溃，代表发生闪退，比对闪退时间与第几次进教室相近；程序卡死，则比对AS里正常退出教室的时间与第几次进教室时间相近则为最终承受次数

        num = 1

        while True:
            timeStr = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
            print("时间：",timeStr," 第 ",str(num)," 次进入教室")
            num += 1
            os.system("adb shell input tap " + str(self.enterRoomX) +  " " + str(self.enterRoomY)) #进入教室
            time.sleep(self.waitTime) #进教室休眠时间
            os.system("adb shell input keyevent 4")
            time.sleep(1)
            os.system("adb shell input tap " + str(self.quitRoomX) +  " " + str(self.quitRoomY)) #退出教室确认
            time.sleep(4)

AutoEnterRoom().start()