#coding=utf-8

import unittest

import HTMLTestRunner
import time
from appium import webdriver
from selenium.webdriver.support.wait import WebDriverWait

CONNECT = {
    'platformName': 'Android',
    'platformVersion': '6.0',
    'deviceName': 'emulator-5554',
    'appPackage': 'com.fudaojun.app.teacher',
    'appActivity': '.activity.loading.LoadingActivity',
    "baseUrl": "http://localhost:4723/wd/hub"
}

# 每个测试用例完成之后都会执行tearDown，然后重新setUp
# 会执行继承 unittest.TestCase 的每个类下的每个 test 开头的方法
class ResetEveryTime(unittest.TestCase):
    u"""登录模块（每次重置）"""

    def setUp(self):
        desired_caps = {
            'platformName': CONNECT['platformName'],
            'platformVersion': CONNECT['platformVersion'],
            'deviceName': CONNECT['deviceName'],
            'appPackage': CONNECT['appPackage'],
            'appActivity': CONNECT['appActivity']
        }
        self.driver = webdriver.Remote(CONNECT['baseUrl'], desired_caps)

    def tearDown(self):
        self.driver.close_app()
        self.driver.quit()

    def test1_skip_guide(self):
        #html报告中显示注释信息
        u"""每次重置-跳过引导页"""
        WebDriverWait(self.driver, 10, 0.5).until(lambda view: view.find_element_by_id("com.fudaojun.app.teacher:id/tv_skip_guide_activity")).click()

    def test2_click_login(self):
        u"""每次重置-点击登录按钮"""
        WebDriverWait(self.driver, 10, 0.5).until(lambda view: view.find_element_by_id("com.fudaojun.app.teacher:id/rlv_button_login")).click()

#只初始化一次
class ResetOnce(unittest.TestCase):
    u"""登录模块（重置一次）"""

    @classmethod
    def setUpClass(self):
        desired_caps = {
            'platformName': CONNECT['platformName'],
            'platformVersion': CONNECT['platformVersion'],
            'deviceName': CONNECT['deviceName'],
            'appPackage': CONNECT['appPackage'],
            'appActivity': CONNECT['appActivity']
        }
        self.driver = webdriver.Remote(CONNECT['baseUrl'], desired_caps)

    @classmethod
    def tearDownClass(self):
        self.driver.quit()

    def test1_skip_guide(self):
        u"""跳过引导页"""
        print("test1_skip_guide")
        WebDriverWait(self.driver, 10, 0.5).until(lambda view: view.find_element_by_id("com.fudaojun.app.teacher:id/tv_skip_guide_activity")).click()
        u'跳过引导页'

    def test2_click_login(self):
        u"""点击登录按钮"""
        print("test2_click_login")
        WebDriverWait(self.driver, 10, 0.5).until(lambda view: view.find_element_by_id("com.fudaojun.app.teacher:id/rlv_button_login")).click()



if __name__ == '__main__':

    suite1 = unittest.TestLoader().loadTestsFromTestCase(ResetEveryTime)
    suite2 = unittest.TestLoader().loadTestsFromTestCase(ResetOnce)
    alltest = unittest.TestSuite([suite1, suite2])

    # 运行
    # unittest.TextTestRunner(verbosity=2).run(alltest) # verbosity 参数可以控制输出的错误报告的详细程度，默认是 1，如果设为 0，则不输出每一用例的执行结果；如果设为 2，则输出详细的执行结果

    # GitHub 上的 HtmlTestRunner：https://github.com/oldani/HtmlTestRunner
    # 逐个 class 生成 html 报告
    # unittest.main(testRunner=HtmlTestRunner.HTMLTestRunner(output='my_dir',
    #                                                        report_title='测试报告标题',
    #                                                        descriptions='测试报告描述'))

    #网上常见的 HTMLTestRunner 安装方法：
    #1. 下载 HTMLTestRunner 文件
    #2. Python 环境下查看安装目录：命令行：python --> import sys --> sys.path。可以看到当前 python 环境的 site-packages 目录
    #3. 新建文件夹HTMLTestRunner，把 HTMLTestRunner.py 文件移动到文件夹内，并新建一个__init__.py文件，此时HTMLTestRunner文件夹就被python解释器认为是可引用的模块
    #4. 将 HTMLTestRunner 文件夹拷贝到路径 .../site-packages/下即可
    #5. import HTMLTestRunner 不报错即可。
    #6. 需要注意，在 Pycharm 里直接点运行并不会生成 html 报告。需要在命令行里执行 python AppiumWithUnittest.py 才会生成报告

    #网上常见的 HTMLTestRunner，会将所有class 汇总到你指定的 html 文件中，只生成一个报告
    timestr = time.strftime('%Y-%m-%d_%H-%M-%S',time.localtime(time.time()))
    fp = open("for_my_love_" + timestr + ".html", 'wb')
    runner = HTMLTestRunner.HTMLTestRunner(
            stream=fp,
            title='小娜娜你好呀',
            description='今晚月色很美'
        )
    runner.run(alltest)
    #执行完成要关闭流，否则 html 文件内容为空
    fp.close()
