# -*- coding: utf-8 -*-
# time: 2023/2/5 3:06
# file: scheduler.py
# author: LuoXishuang(https://github.com/LuoXishuang0712/)
import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from croniter import croniter, CroniterNotAlphaError, CroniterBadCronError


class SchedulerHandler:
    scheduler = None
    default_url = "sqlite:///scheduler.sqlite"

    def __init__(self, url: str = None):
        self.scheduler = BackgroundScheduler()

        url = url or self.default_url
        self.scheduler.add_jobstore('sqlalchemy', url=url)

    @staticmethod
    def __deal_cron_str(cron):
        try:
            croniter(cron, start_time=datetime.datetime.now())
        except CroniterNotAlphaError as e:
            raise RuntimeError(e)
        except CroniterBadCronError as ignored:  # year check problem
            pass

        cron_split = cron.split(" ")
        keys = ["second", "minute", "hour", "day", "month", "day_of_week", "year"]
        kwargs = {keys[i]: cron_split[i] for i in range(len(cron_split))}

        return kwargs

    def add_job(self, func, args, cron: str, job_id):
        kwargs = self.__deal_cron_str(cron)

        self.scheduler.add_job(func, 'cron', **kwargs, args=args, timezone='Asia/Shanghai', id=job_id)

    def reschedule_job(self, job_id, cron):
        kwargs = self.__deal_cron_str(cron)

        self.scheduler.reschedule_job(job_id, timezone='Asia/Shanghai', trigger='cron', **kwargs)

    def start(self):
        self.scheduler.start()

    def shutdown(self):
        self.scheduler.shutdown()

    def get_job(self, job_id):
        return self.scheduler.get_job(job_id)

    def get_job_list(self):
        return self.scheduler.get_jobs()

    def remove_job(self, job_id):
        self.scheduler.remove_job(job_id)

    # def __del__(self):
    #     self.shutdown()
