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

    # 跳过引导页
    def test1_skip_guide(self):
        WebDriverWait(self.driver, 10, 0.5).until(lambda view: view.find_element_by_id("com.fudaojun.app.teacher:id/tv_skip_guide_activity")).click()

    # 点击登录按钮
    def test2_click_login(self):
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

    # 跳过引导页
    def test1_skip_guide(self):
        print("test1_skip_guide")
        WebDriverWait(self.driver, 10, 0.5).until(lambda view: view.find_element_by_id("com.fudaojun.app.teacher:id/tv_skip_guide_activity")).click()
        u'跳过引导页'

    # 点击登录按钮
    def test2_click_login(self):
        print("test2_click_login")
        WebDriverWait(self.driver, 10, 0.5).until(lambda view: view.find_element_by_id("com.fudaojun.app.teacher:id/rlv_button_login")).click()



if __name__ == '__main__':
    unittest.main(testRunner=HtmlTestRunner.HTMLTestRunner(output='my_dir',
                                                           report_title='测试报告标题',
                                                           descriptions='测试报告描述'))

    # suite1 = unittest.TestLoader().loadTestsFromTestCasese(ResetEveryTime)
    # suite2 = unittest.TestLoader().loadTestsFromTestCase(ResetOnce)
    # alltest = unittest.TestSuite([suite1,suite2])
    #verbosity 参数可以控制输出的错误报告的详细程度，默认是 1，如果设为 0，则不输出每一用例的执行结果；如果设为 2，则输出详细的执行结果
    # unittest.TextTestRunner(verbosity=2).run(suite2)