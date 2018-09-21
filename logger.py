#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2018/9/19 上午9:50
# @Author  : huangjie
# @Site    : 
# @File    : logger.py
# @Software: PyCharm

import logging.handlers
import os

LOG_FOLDER = 'log'
path = os.path.join(os.path.dirname(__file__), LOG_FOLDER)
LOG_FILE = path + '/server_info.log'

# 判断文件夹是否存在，不存在则创建
if not os.path.exists(path):
    os.makedirs(path)

handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=1024 * 1024)
fmt = '%(asctime)s - %(filename)s:%(lineno)s - %(name)s - %(message)s'

formatter = logging.Formatter(fmt)
handler.setFormatter(formatter)

logger = logging.getLogger('server_info')
logger.addHandler(handler)
logger.setLevel(logging.INFO)
