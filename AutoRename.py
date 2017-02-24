# encoding: utf-8
import shutil
import os,sys

# 改名脚本：UI提供的图都带有@2x，@3x字样，无法放入android资源文件夹中。
# 脚本的作用就是去除非法字符并分类
for fileName in os.listdir(sys.path[0]):
    if fileName.find("@2x") >= 0:
        if os.path.exists("2倍") == False:
            os.mkdir("2倍")
        newFileName = fileName.replace("@2x", "")
        os.renames(fileName, newFileName)
        shutil.move(newFileName,"2倍" + "/" + newFileName)

    elif fileName.find("@3x") >= 0:
        if os.path.exists("3倍") == False:
            os.mkdir("3倍")
        newFileName = fileName.replace("@3x", "")
        os.renames(fileName, newFileName)
        shutil.move(newFileName,"3倍" + "/" + newFileName)
