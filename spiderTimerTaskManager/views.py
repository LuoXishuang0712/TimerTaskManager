# -*- coding: utf-8 -*-
# time: 2023/2/5 1:49
# file: views.py.py
# author: LuoXishuang(https://github.com/LuoXishuang0712/)
import datetime
import json

from functools import wraps

from apscheduler.triggers.cron import CronTrigger
from django.contrib.auth import authenticate, login
from django.shortcuts import render
from django.http.request import HttpRequest
from django.http.response import Http404, JsonResponse

from .scheduler import SchedulerHandler

time_format = "%Y-%m-%d %H:%M:%S"

scheduler = SchedulerHandler("sqlite:///test.sqlite")
scheduler.start()

last_error = {}
last_run = {}


def run_job(code, job_id):
    last_run[job_id] = datetime.datetime.now()
    try:
        exec(code)
    except BaseException as e:
        last_error[job_id] = e


def get_crontab(trigger):
    field_key = ('year', 'month', 'day', 'week', 'day_of_week', 'hour', 'minute', 'second')
    to_keys = ["second", "minute", "hour", "day", "month", "day_of_week", "year"]
    field_map = {field_key[i]: str(trigger.fields[i]) for i in range(len(trigger.fields))}
    return " ".join([field_map[i] for i in to_keys])


def dashboard(req: HttpRequest):
    ctx = dict()
    ctx['test'] = 'Hello World'
    return render(req, 'dashboard.html', ctx)


def request_method_check(method: str):
    def check(func):
        @wraps(func)
        def wrap(req: HttpRequest, *args, **kwargs):
            if req.method != method:
                raise Http404("please request from %s method" % method)

            return func(req, *args, **kwargs)
        return wrap
    return check


def login_check(func):
    @wraps(func)
    def wrap(req: HttpRequest, *args, **kwargs):
        if not req.user.is_authenticated:
            return JsonResponse({"status": False, "msg": "please login first"})

        return func(req, *args, **kwargs)
    return wrap


@login_check
@request_method_check('GET')
def api_scheduler_list(req: HttpRequest):
    task_list = []
    for job in scheduler.get_job_list():
        task_list.append({
            "id": job.id,
            "last": last_run[job.id].strftime(time_format) if job.id in last_run else None,
            "cron": isinstance(job.trigger, CronTrigger) and get_crontab(job.trigger) or "Not a CRON trigger",
            "error": str(last_error[job.id]) if job.id in last_error else None,
            "next": job.next_run_time.strftime(time_format) if job.next_run_time else None,
        })
        # job.pause()
    return JsonResponse({"status": True, "msg": "fetch success", "data": task_list})


@login_check
@request_method_check('POST')
def api_scheduler_add(req: HttpRequest):
    try:
        req_json = json.loads(req.body)
    except json.decoder.JSONDecodeError as ignored:
        return JsonResponse({"status": False, "msg": "not a valid json string"})

    if "id" not in req_json or \
            "cron" not in req_json or \
            "code" not in req_json:
        return JsonResponse({"status": False, "msg": "missing necessary request field"})

    try:
        scheduler.add_job(run_job, [req_json["code"], req_json["id"]], req_json["cron"], req_json["id"])
    except RuntimeError:
        return JsonResponse({"status": False, "msg": "not a valid cron expression"})

    return JsonResponse({"status": True, "msg": "test success"})


@login_check
@request_method_check('POST')
def api_change_job_status(req: HttpRequest):
    try:
        req_json = json.loads(req.body)
    except json.decoder.JSONDecodeError as ignroed:
        return JsonResponse({"status": False, "msg": "not a valid json string"})

    if "id" not in req_json or \
            "command" not in req_json:
        return JsonResponse({"status": False, "msg": "missing necessary request field"})

    job = scheduler.get_job(req_json["id"])
    if job is None:
        return JsonResponse({"status": False, "msg": "not a valid job id"})

    try:
        if req_json["command"] == "pause":
            job.pause()
        elif req_json["command"] == "resume":
            job.resume()
        elif req_json["command"] == "delete":
            scheduler.remove_job(req_json["id"])
        else:
            return JsonResponse({"status": False, "msg": "not a valid action command"})
    except BaseException:
        return JsonResponse({"status": False, "msg": "cannot do such action to job"})

    return JsonResponse({"status": True, "msg": "action command executed successfully"})


@request_method_check('POST')
def api_sign_in(req: HttpRequest):
    try:
        req_json = json.loads(req.body)
    except json.decoder.JSONDecodeError as ignroed:
        return JsonResponse({"status": False, "msg": "not a valid json string"})

    if "username" not in req_json or \
            "password" not in req_json:
        return JsonResponse({"status": False, "msg": "missing necessary request field"})

    user = authenticate(req, username=req_json["username"], password=req_json["password"])

    if user is None:
        return JsonResponse({"status": False, "msg": "a wrong username or password"})

    login(req, user)
    return JsonResponse({"status": True, "msg": "login successfully"})


@request_method_check('GET')
def api_check_login(req: HttpRequest):
    if not req.user.is_authenticated:
        return JsonResponse({"status": False, "msg": "not a logged session"})
    return JsonResponse({"status": True, "msg": "a logged session"})
