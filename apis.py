#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2018/9/19 下午3:32
# @Author  : huangjie
# @Site    : 
# @File    : apis.py
# @Software: PyCharm

class APIError(Exception):
    """"""

    def __init__(self, error, field='', message=''):
        """Constructor for APIError"""
        super(APIError, self).__init__(message)
        self.error = error
        self.field = field
        self.message = message
