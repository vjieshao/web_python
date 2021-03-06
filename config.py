#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2018/9/11 上午10:35
# @Author  : huangjie
# @Site    : 
# @File    : config.py
# @Software: PyCharm

import config_default
import config_override


class Dict(dict):
    """"""

    def __init__(self, names=(), values=(), **kw):
        """Constructor for """
        super(Dict, self).__init__(**kw)
        for k, v in zip(names, values):
            self[k] = v

    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError:
            raise AttributeError(r"'Dict' object has no attribute '%s' " % item)

    def __setattr__(self, key, value):
        self[key] = value


def merge(default, override):
    r = {}
    for k, v in default.items():
        if k in override:
            if isinstance(v, dict):
                r[k] = merge(v, override[k])
            else:
                r[k] = override[k]
        else:
            r[k] = v
    return r


def toDict(d):
    D = Dict()
    for k, v in d.items():
        D[k] = toDict(v) if isinstance(v, dict) else v
    return D


try:
    configs = merge(config_default.configs, config_override.configs)
except ImportError:
    pass

configs = toDict(configs)
