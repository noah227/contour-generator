# -*- coding: utf-8 -*-
# CREATED: 2023/4/18
# AUTHOR : NOAH YOUNG
# EMAIL  : noah227@foxmail.com

import datetime
import json
import multiprocessing
import os
import re
import time

import cv2
import matplotlib.pyplot as plt
import numpy as np


def decCountTimeConsume(func):
    """
    计时装饰器
    """

    def inner(*args, **kwargs):
        print(f"{datetime.datetime.today()} | {func.__name__}开始执行")
        log(f"{datetime.datetime.today()} | {func.__name__}开始执行")
        startTime = time.time()
        func(*args, **kwargs)
        endTime = time.time()
        timeConsumed = endTime - startTime
        print(f"{datetime.datetime.today()} | {func.__name__}执行结束，共耗时{timeConsumed}秒")
        log(f"{datetime.datetime.today()} | {func.__name__}执行结束，共耗时{timeConsumed}秒")

    return inner


def log(s):
    """
    输出日志，按日期命名
    """
    if not os.path.isdir("./log"):
        os.mkdir("./log")
    with open(f"./log/log-{datetime.datetime.today().strftime('%Y-%m-%d')}", "a+", encoding="utf8") as f:
        f.write(f"{s}\n")


class ContourGenerator:
    def __init__(self, thresh=100, threshMaxVal=255, fillColor=0, strokeColorRGBA=(0, 255, 255, 255),
                 maxProcesses=None):
        """
        初始化配置
        :param thresh: 用于二值化处理cv2.threshold的参数thresh
        :param threshMaxVal: 用于二值化处理cv2.threshold的参数maxval
        :param fillColor: 生成图的填充色
        :param strokeColorRGBA: 线条填充色
        :param maxProcesses: 处理时的最大进程数
        """
        self.thresh = thresh
        self.threshMaxVal = threshMaxVal
        self.fillColor = fillColor
        self.strokeColorRGBA = strokeColorRGBA
        self.transparent = True if self.fillColor == 0 else False
        self.maxProcesses = maxProcesses if maxProcesses else os.cpu_count()
        pass

    @decCountTimeConsume
    def generateFromVideo(self, videoPath, outputDir=None, extension=".svg", generateAbstractData=None):
        """
        从视频文件生成，逐帧读取，使用多进程
        :param videoPath: 视频路径
        :param outputDir: 视频类的转换会输出到文件夹
        :param extension: 指定输出文件类型（默认.svg）
        :param generateAbstractData: 是否生成数据内容清单
        :return: None
        """
        cap = cv2.VideoCapture(videoPath)
        count = 0
        if not cap.isOpened():
            return
        # 输出文件夹
        if not outputDir:
            outputDir = re.sub(r"\.\w+", "", os.path.basename(videoPath))
            # 视频的暂且存储在指定的路径，不使用原地输出策略
            outputDir = f"./xports/{outputDir}"
            if not os.path.exists(outputDir):
                os.mkdir(outputDir)
        # 进程池建立
        processPool = multiprocessing.Pool(self.maxProcesses)
        while True:
            # 读取帧
            ret, frame = cap.read()
            if not ret:
                cap.release()
                break
            else:
                processPool.apply_async(self.generateFromImage, (None, frame, f"{count + 1}", outputDir, extension))
                count += 1
        processPool.close()
        processPool.join()
        # 输出摘要信息
        if generateAbstractData:
            with open(os.path.join(outputDir, "data.json"), "w", encoding="utf8") as f:
                f.write(json.dumps({"total": count + 1}, indent=4))
        pass

    def generateFromImage(self, imgPath=None, img=None, outputFileName=None, outputDir=None, extension=".svg"):
        """
        从图片生成
        :param imgPath: 图片路径
        :param img: 图片数据
        :param outputFileName: 输出文件名
        :param outputDir: 输出文件夹
        :param extension: 指定输出文件类型（默认.svg）
        :return: None
        """
        if imgPath is None and img is None:
            return
        contouredData = self.__generateContouredData(imgPath, img=img)
        plt.imsave(self.__getOutputPath(imgPath, outputFileName, outputDir, extension), contouredData)
        pass

    @staticmethod
    def __getOutputPath(filePath, outputFileName=None, outputDir=None, extension=".svg"):
        """
        获取文件输出路径，默认原位置输出
        :param filePath: 文件路径
        :param outputFileName: 指定输出文件名
        :param outputDir: 指定输出文件夹
        :param extension: 指定输出文件类型（默认.svg）
        :return:
        """
        # todo 不用担心指定扩展类型原位置输出时文件名可能出现的冲突问题，交互式应用会提示
        dirname = outputDir if outputDir else os.path.dirname(filePath)
        if outputFileName:
            filename = outputFileName
        else:
            filename = os.path.basename(filePath)
            filename = re.sub(r"\.\w+$", "", filename)
        return os.path.join(dirname, f"{filename}{extension}")
        pass

    def __generateContouredData(self, imgPath=None, img=None):
        """
        获取边界数据
        :param imgPath: 图片路径
        :param img: 图片数据（存在时优先于从路径读取）
        :return: 图片边界数据
        """
        img = img if img is not None else cv2.imread(imgPath) if imgPath else None
        if img is None:
            raise TypeError("imgPath or img is needed!")
        # 灰度转换
        imgGary = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # 二值化处理
        ret, imgThreshed = cv2.threshold(imgGary, self.thresh, self.threshMaxVal, cv2.THRESH_BINARY)
        # 获取边界数据
        contours, hierarchy = cv2.findContours(imgThreshed, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        # 创建背景（设置为空白背景时创建4通道）
        channels = 4 if self.transparent else 3
        imgEmpty = np.zeros((*img.shape[:2], channels), np.uint8)
        # 0即使填充也不影响
        imgEmpty.fill(self.fillColor)
        # 图像颜色模式转换
        imgEmpty = cv2.cvtColor(imgEmpty, cv2.COLOR_BGR2RGBA)
        # 绘制边界
        imgThreshedAndContoured = cv2.drawContours(imgEmpty, contours, -1, self.strokeColorRGBA, 1)

        return imgThreshedAndContoured


if __name__ == "__main__":
    cg = ContourGenerator()
    cg.generateFromVideo("./videos/SampleVideo_1280x720_1mb.mp4")
    # cg.generateFromImage("./images/totoro.png")
    # print(os.path.dirname("./images/totoro.png"))
    # ContourGenerator().generateFromImage()
    pass
