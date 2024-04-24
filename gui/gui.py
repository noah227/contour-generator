# -*- coding: utf-8 -*-
# CREATED: 2024/4/3
# AUTHOR : NOAH YOUNG
# EMAIL  : noah227@foxmail.com

import os
import time
import tkinter as tk
import tkinter.filedialog

import webview

from main import ContourGenerator


class JsApi:
    def __init__(self):
        # 原始输入位置
        self.imgSource = ""
        self.imgCurrent = ""
        self.threshold = 100
        self.prepare()

    @staticmethod
    def prepare():
        if not os.path.exists("temp"):
            os.mkdir("temp")
        pass

    def syncControls(self, data):
        action = data.get("action")
        threshold = data.get("threshold")

        if not self.imgSource:
            return self.renderSelectedSingleImage()

        print("SYNC", threshold, self.imgSource)
        self.threshold = int(threshold) if threshold else self.threshold
        if action == "update":
            return self.processImage()

        elif action == "select":
            return self.renderSelectedSingleImage()
        elif action == "save-single":
            return self.saveSingleImage()

        # ContourGenerator(thresh=threshold).generateFromImage(imgPath="./110901.jpg")
        # return "./110901.svg" + f"?t={time.time()}"

    def renderSelectedSingleImage(self):
        root = tk.Tk()
        root.withdraw()
        file = tkinter.filedialog.askopenfilename()
        root.destroy()

        if file:
            self.imgSource = file
            return self.processImage()
        else:
            return
        pass

    def processImage(self):
        # 复制到临时文件夹
        # 处理图片
        ContourGenerator(thresh=self.threshold).generateFromImage(imgPath=self.imgSource, outputDir="./temp",
                                                                  outputFileName="temp")
        return self.processReturn()
        pass

    @staticmethod
    def getFileExt(basename):
        return basename.split(".")[-1]

    def processReturn(self, ext="svg"):
        self.imgCurrent = f"./temp/temp.{ext}"
        return f"{self.imgCurrent}?t={time.time()}"

    def saveSingleImage(self):
        if self.imgCurrent:
            root = tk.Tk()
            root.withdraw()
            saveFile = tkinter.filedialog.asksaveasfilename()
            root.destroy()
            if saveFile:
                import shutil
                shutil.copyfile(self.imgCurrent, saveFile)
                pass
        pass


if __name__ == '__main__':
    webview.create_window("hello", "./index.html", js_api=JsApi(), width=960, height=600)
    webview.start(debug=True)
    # root = tk.Tk()
    # root.withdraw()
    # filename = tkinter.filedialog.askopenfilename()
    # print(filename, "<<<")
    # print(os.path.basename("E:/Documents/test/sqllite-test/utils.py"))

    pass
