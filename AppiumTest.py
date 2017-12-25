# coding=utf-8

from appium import webdriver
from selenium.webdriver.support.wait import WebDriverWait

desired_caps = {}
desired_caps['platformName'] = 'Android'
desired_caps['platformVersion'] = '6.0'
desired_caps['deviceName'] = 'emulator-5554'
# 想要打开的 app 的包名和启动页，包名可通过 uiautomatorviewer 获取
# 启动页 activity 通过命令 adb logcat | grep Displayed 获取(该命令可获取当前activity，如果出现多个，第一个即为启动activity）
desired_caps['appPackage'] = 'com.fudaojun.app.teacher'
desired_caps['appActivity'] = '.activity.loading.LoadingActivity'

# python 连接 appium
driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)

# 网上常见这种写法：driver.find_element_by_accessibility_id("com.fudaojun.app.teacher:id/rlv_button_login").click()
# 但是运行会报 An element could not be located on the page using the given search parameters.
# 字面上理解是元素未在页面中找到，但明明 id 就是正确的。所以可能导致的原因是因为代码执行到时该元素还未被加载。故要换一种
# 写法，需要在使用元素前先等待元素加载完成

# 不知道为啥，每次都会进入引导页。点击跳过引导页
WebDriverWait(driver, 10, 0.5).until(lambda view: view.find_element_by_id("com.fudaojun.app.teacher:id/tv_skip_guide_activity")).click()

# 点击登录按钮
WebDriverWait(driver, 10, 0.5).until(lambda view: view.find_element_by_id("com.fudaojun.app.teacher:id/rlv_button_login")).click()

# 如果运行真机时使用 uiautomatorviewer 报错 Error while obtaining UI hierarchy XML file: com.android.ddmlib.SyncException: Remote object doesn't exist!
# 尝试运行虚拟机时使用。

print("for my love")
