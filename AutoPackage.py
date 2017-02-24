# encoding: utf-8
import shutil
import os

# 需求：市场那边要求各渠道分文件夹
# 该脚本作用是将各个渠道包移动到所属渠道文件夹中
class myApk(object):
    def __init__(self, apkname, dirname):
        self.apkname = apkname
        self.dirname = dirname

myApks = [myApk("app-a91-release.apk", "91市场"),
          myApk("app-a360-release.apk", "360手机助手"),
          myApk("app-anzhi-release.apk", "安智市场"),
          myApk("app-anzhuo-release.apk", "安卓市场"),
          myApk("app-baidu-release.apk", "百度应用"),
          myApk("app-baidufufei-release.apk", "百度付费推广"),
          myApk("app-bdsousuo-release.apk", "百度搜索付费"),
          myApk("app-guanfang-release.apk", "官方包"),
          myApk("app-huawei-release.apk", "华为应用市场"),
          myApk("app-lianxiang-release.apk", "联想乐商店"),
          myApk("app-meizu-release.apk", "魅族应用市场"),
          myApk("app-oppo-release.apk", "oppo应用市场"),
          myApk("app-tencent_guangdiantong-release.apk", "腾讯广点通"),
          myApk("app-vivo-release.apk", "vivo应用市场"),
          myApk("app-wandoujia-release.apk", "豌豆荚"),
          myApk("app-xiaomi-release.apk", "小米市场"),
          myApk("app-xiaoqudao-release.apk", "小渠道公共包"),
          myApk("app-yingyongbao-release.apk", "应用宝"),
          myApk("app-yingyongbao1-release.apk", "应用宝1"),
          ]

# 自动生成对应渠道的文件夹
def move_file(apkname, dirname):
    if(os.path.exists(apkname)):
        os.mkdir(dirname)
        shutil.move(apkname,dirname + "/" + apkname)
    else :
        if(os.path.exists(dirname) == False):
            print apkname + "不存在"

for x in myApks:
    move_file(x.apkname, x.dirname)
