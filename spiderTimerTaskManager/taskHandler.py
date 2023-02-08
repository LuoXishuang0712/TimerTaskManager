# -*- coding: utf-8 -*-
# time: 2023/2/7 23:00
# file: taskHandler.py
# author: LuoXishuang(https://github.com/LuoXishuang0712/)
import datetime


class TaskHandler:
    def __init__(self, code):
        self.code = code
        self.last_run = None
        self.last_error = None

    def run(self):
        self.last_run = datetime.datetime.now()
        try:
            exec(self.code)
        except BaseException as e:
            self.last_error = e

    def __call__(self, scheduled=True):
        if scheduled:
            self.run()
        else:
            return self
