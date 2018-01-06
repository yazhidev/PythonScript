#coding=utf-8

import unittest

import HtmlTestRunner
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
    alltest = unittest.TestSuite([suite1,suite2])
    #verbosity 参数可以控制输出的错误报告的详细程度，默认是 1，如果设为 0，则不输出每一用例的执行结果；如果设为 2，则输出详细的执行结果
    # unittest.TextTestRunner(verbosity=2).run(alltest)
    # 逐个 class 生成 html 报告
    # unittest.main(testRunner=HtmlTestRunner.HTMLTestRunner(output='my_dir',
    #                                                        report_title='测试报告标题',
    #                                                        descriptions='测试报告描述'))

    fp = open("test.html", 'wb')
    runner = HtmlTestRunner.HTMLTestRunner(
        output='my_dir',
        stream=fp,
        report_title='测试结果',
        descriptions='测试报告'
    )
    runner.run(alltest)
    fp.close() #测试报告关闭



    # suite1 = unittest.TestLoader().loadTestsFromTestCasese(ResetEveryTime)
    # suite2 = unittest.TestLoader().loadTestsFromTestCase(ResetOnce)
    # alltest = unittest.TestSuite([suite1,suite2])
    #verbosity 参数可以控制输出的错误报告的详细程度，默认是 1，如果设为 0，则不输出每一用例的执行结果；如果设为 2，则输出详细的执行结果
    # unittest.TextTestRunner(verbosity=2).run(suite2)