# encoding: utf-8
import shutil
import os,sys

# 改名脚本：UI提供的图都带有@2x，@3x字样，无法放入android资源文件夹中。
# 脚本的作用就是去除非法字符并分类
multiple1 = "@1x"
multiple1dirName = "1倍_m"
multiple2 = "@2x"
multiple2dirName = "2倍_x"
multiple3 = "@3x"
multiple3dirName = "3倍_xx"

for fileName in os.listdir(sys.path[0]):
    if fileName.find(multiple2) >= 0:
        if os.path.exists(multiple2dirName) == False:
            os.mkdir(multiple2dirName)
        newFileName = fileName.replace(multiple2, "")
        os.renames(fileName, newFileName)
        shutil.move(newFileName,multiple2dirName + "/" + newFileName)

    elif fileName.find(multiple3) >= 0:
        if os.path.exists(multiple3dirName) == False:
            os.mkdir(multiple3dirName)
        newFileName = fileName.replace(multiple3, "")
        os.renames(fileName, newFileName)
        shutil.move(newFileName,multiple3dirName + "/" + newFileName)

    else:
        # 不带倍数，即为1倍
        if fileName.find("AutoRename") < 0:
            if os.path.exists(multiple1dirName) == False :
                os.mkdir(multiple1dirName)
            shutil.move(fileName,multiple1dirName + "/" + fileName)