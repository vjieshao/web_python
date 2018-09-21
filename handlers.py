#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2018/9/19 上午10:07
# @Author  : huangjie
# @Site    : 
# @File    : handlers.py
# @Software: PyCharm

from web_framework import get, post


def get_page_index(page_str):
    p = 1
    try:
        p = int(page_str)
    except ValueError as e:
        pass
    if p < 1:
        p = 1
    return p


@get('/')
async def index(*, page='1'):
    print(page)
    page_index = get_page_index(page)
    return {
        '__template__': 'blogs.html',
        'page': page
    }