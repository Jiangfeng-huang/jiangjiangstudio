#!/bin/bash
# 激活虚拟环境
source /root/pdm_system/venv/bin/activate
# 运行Django服务器
cd /root/pdm_system
python manage.py runserver 0.0.0.0:8000
