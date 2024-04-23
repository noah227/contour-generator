# -*- coding: utf-8 -*-
# CREATED: 2024/4/3
# AUTHOR : NOAH YOUNG
# EMAIL  : noah227@foxmail.com

import tkinter as tk
import os
import webview
from main import ContourGenerator
import time


class JsApi:
    def syncControls(self, threshold=100):
        print("SYNC", threshold)
        threshold = int(threshold)
        ContourGenerator(thresh=threshold).generateFromImage(imgPath="./totoro.png")
        return "./totoro.svg" + f"?t={time.time()}"
        ContourGenerator(thresh=threshold).generateFromImage(imgPath="./110901.jpg")
        return "./110901.svg" + f"?t={time.time()}"



if __name__ == '__main__':
    webview.create_window("hello", "./index.html", js_api=JsApi(), width=720, height=520)
    webview.start(debug=True)
    pass
