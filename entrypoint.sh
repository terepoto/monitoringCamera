#!/bin/sh

uwsgi --socket :8001 --module monitoringCamera.wsgi --py-autoreload 1 --logto /var/www/html/log.log