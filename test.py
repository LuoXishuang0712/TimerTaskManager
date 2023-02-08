# -*- coding: utf-8 -*-
# time: 2023/2/5 3:41
# file: test.py
# author: LuoXishuang(https://github.com/LuoXishuang0712/)
import time

import requests

from spiderTimerTaskManager.scheduler import SchedulerHandler


def job(message):
    requests.get("http://localhost:8000/")


def get_crontab(trigger):
    field_key = ('year', 'month', 'day', 'week', 'day_of_week', 'hour', 'minute', 'second')
    to_keys = ["second", "minute", "hour", "day", "month", "day_of_week", "year"]
    field_map = {field_key[i]: str(trigger.fields[i]) for i in range(len(trigger.fields))}
    return " ".join([field_map[i] for i in to_keys])


if __name__ == '__main__':
    scheduler = SchedulerHandler("sqlite:///test.sqlite")
    scheduler.start()
    scheduler.reschedule_job("network_request", "*/15 * * * * *")
    print([
        i.func
        for i in scheduler.get_job_list()
    ])
    # cnt = 0
    # while True:
    #     cnt += 1
    #     time.sleep(1)
    #     if cnt >= 15:
    #         break
    # scheduler.shutdown()
