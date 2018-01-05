#coding=utf-8

import unittest

from appium import webdriver

from appiumDir import AppConfig


class AppTestCase(unittest.TestCase):
    def setUp(self):
        desired_caps = {
            'platformName': AppConfig.CONNECT['platformName'],
            'platformVersion': AppConfig.CONNECT['platformVersion'],
            'deviceName': AppConfig.CONNECT['deviceName'],
            'appPackage': AppConfig.CONNECT['appPackage'],
            'appActivity': AppConfig.CONNECT['appActivity']
        }
        self.driver = webdriver.Remote(AppConfig.CONNECT['baseUrl'], desired_caps)

    def tearDown(self):
        self.driver.quit()
