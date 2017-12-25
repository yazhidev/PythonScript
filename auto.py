from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time
import re

crm_address = 'http://121.40.44.94/'

"""
xpath: "//*[@id='sidebar-menu']/div/ul[3]/li/ul" ==> '我的联系人'相对路径
"""
#等待时间 等待网页加载的时间
# if not None 或者 if not False 相当于True
def wait_for_appear(browser, name, name_type=None, timeout=None):
    if not timeout:
        timeout = 10     #没有传入的时间就默认设为10秒
    if not name_type:
        name_type = By.ID     #没有传入的值就根据ID获取
    try:
        WebDriverWait(browser, timeout).until(
            EC.presence_of_element_located((name_type, name))
        )
    except Exception as error:
        raise error

def setup():
    # 取得 chromedriver 地址
    chromedriver_address = os.path.join(os.getcwd(), 'chromedriver')
    browser = webdriver.Chrome(chromedriver_address)
    browser.maximize_window()
    # browser.set_window_size(1875, 1680)
    browser.get(crm_address)

    # 登陆
    wait_for_appear(browser, 'username', By.ID)
    username = browser.find_element_by_id('username')     #找到这个输入框
    username.send_keys('admin')            # .send_keys('') 向其中输入值
    password = browser.find_element_by_id('password')
    password.send_keys('123456789')
    browser.find_element_by_id("submit").click()    #找到按钮并点击 .click()

    #等到检测到指定的元素 //*[@id=\'sidebar-menu\']/div/ul[3]/li/ul 进行下一步
    wait_for_appear(browser, '//*[@id=\'sidebar-menu\']/div/ul[5]/li/ul', name_type=By.XPATH, timeout=20)
    print('ok')

    # 关闭Hide按钮(限测试环境，生产环境需判断)
    browser.find_element_by_id("flHideToolBarButton").click()
    time.sleep(1)
    teacher = browser.find_element_by_xpath("//*[@id='sidebar-menu']/div/ul[4]")
    teacher.click()
    wait_for_appear(browser, '//*[@id=\'sidebar-menu\']/div/ul[4]/li/ul/li[3]', name_type=By.XPATH)
    wait_for_appear(browser, '//*[@id="sidebar-menu"]/div/ul[4]/li/ul/li[3]/a', name_type=By.XPATH)
    print('ok')
    time.sleep(3)

    teacher_search = browser.find_element_by_xpath("//*[@id='sidebar-menu']/div/ul[4]/li/ul/li[3]")
    teacher_search.click()
    teacher_name = browser.find_element_by_id("teacher-name")
    teacher_name.send_keys("谢灵丹")
    button_sure = browser.find_element_by_xpath("//form/div[7]/div/button[2]")
    button_sure.click()

setup()
time.sleep(100000)
