#coding=utf-8

import unittest

from appium import webdriver
from selenium.webdriver.support.wait import WebDriverWait

from appiumDir import AppConfig


class MyTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        print('setUpClass')
        desired_caps = {
            'platformName': AppConfig.CONNECT['platformName'],
            'platformVersion': AppConfig.CONNECT['platformVersion'],
            'deviceName': AppConfig.CONNECT['deviceName'],
            'appPackage': AppConfig.CONNECT['appPackage'],
            'appActivity': AppConfig.CONNECT['appActivity']
        }
        self.driver = webdriver.Remote(AppConfig.CONNECT['baseUrl'], desired_caps)

    @classmethod
    def tearDownClass(self):
        self.driver.quit()
        print('tearDown')


    # def setUp(self):
    #     desired_caps = {
    #         'platformName': AppConfig.CONNECT['platformName'],
    #         'platformVersion': AppConfig.CONNECT['platformVersion'],
    #         'deviceName': AppConfig.CONNECT['deviceName'],
    #         'appPackage': AppConfig.CONNECT['appPackage'],
    #         'appActivity': AppConfig.CONNECT['appActivity']
    #     }
    #     self.driver = webdriver.Remote(AppConfig.CONNECT['baseUrl'], desired_caps)


    # def tearDown(self):
    #     self.driver.close_app()
    #     self.driver.quit()

    # 每个测试用例完成之后都会执行tearDown，然后重新setUp
    # 跳过引导页
    def test1_skip_guide(self):
        print('test_skip_guide')

        WebDriverWait(self.driver, 10, 0.5).until(lambda view: view.find_element_by_id("com.fudaojun.app.teacher:id/tv_skip_guide_activity")).click()

    # 点击登录按钮
    def test2_click_login(self):
        print('test_click_login')

        WebDriverWait(self.driver, 10, 0.5).until(lambda view: view.find_element_by_id("com.fudaojun.app.teacher:id/rlv_button_login")).click()




if __name__ == '__main__':
    # suite = unittest.TestLoader().loadTestsFromTestCase(MyTest)
    # verbosity 参数可以控制输出的错误报告的详细程度，默认是 1，如果设为 0，则不输出每一用例的执行结果；如果设为 2，则输出详细的执行结果
    # unittest.TextTestRunner(verbosity=3).run(suite)

    #使用 setUpClass ，不每次都重置环境
    suite = unittest.TestSuite()
    suite.addTest(MyTest('test1_skip_guide'))
    suite.addTest(MyTest('test2_click_login'))
    unittest.TextTestRunner(verbosity=2).run(suite)

    # suite = unittest.TestSuite()
    # suite.addTest(ContactsAndroidTests("test_name"))
    # timestr = time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
    # filename = '/Users/zengyazhi/Documents/工作/ADB/'+timestr+'.html'
    # fp = open(filename, 'wb')
    # runner = HTMLTestRunner.HTMLTestRunner(
    #     stream=fp,
    #     title='测试结果',
    #     description='测试报告'
    # )
    # runner.run(suite)
    # fp.close() #测试报告关闭