#! /bin/bash

#altere a pasta final para mudar o tipo do programa.

cd /home/pi/app/ve_data_log/serverContagem

.venv/bin/python manage.py runserver 0.0.0.0:8000
