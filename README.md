# TimerTaskManager

***

## introduction

This is a web-server for Python timer task.

By setting CRON trigger on the webpage, this server can run these code in cycle and monitor their running status.

***

## information

* start page: '/dashboard'
* account manager: '/admin' (the built-in user manager by Django)

> create a user  
> run `python manager.py create superuser` and follow the introduction

*** 

## installation

1. install dependencies by `python -m pip install -r requirements.txt`
2. run `python manager.py runserver`

***

## warning

* The server is only be protected by user authentic system, the logged user can run any Python code on your server.
* The access to static files are in DEBUG mode, and cannot use in production environment. (Actually, this project are not be advised using in production.)
* Static files are used for acceleration, you can move them to CDN or redirect by using NGINX.

***

## TODO

* remove static files.
* Python code check.
