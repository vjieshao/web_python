#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2018/9/11 上午9:59
# @Author  : huangjie
# @Site    : 
# @File    : app.py
# @Software: PyCharm

import asyncio
import orm
import time
import os
import json

from aiohttp import web, web_runner
from config import configs
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
from logger import logger
from web_framework import add_routes


async def logger_factory(app, handler):
    async def logger_fact(request):
        logger.info('Request: %s %s' % (request.method, request.path))
        return await handler(request)

    return logger_fact


async def response_factory(app, handler):
    async def response(request):
        logger.info('Response handler...')
        r = await handler(request)
        logger.info('response result = %s' % str(r))

        if isinstance(r, web.StreamResponse):
            return r
        if isinstance(r, bytes):
            resp = web.Response(body=r)
            resp.content_type = 'application/octet-stream'
            return resp
        if isinstance(r, str):
            if r.startswith('redirect:'):
                # 先判断是不是需要重定向，是的话直接用重定向的地址重定向
                return web.HTTPFound(r[9:])
            resp = web.Response(body=r.encode('utf-8'))
            resp.content_type = 'text/html;charset=utf-8'
            return resp
        if isinstance(r, dict):
            template = r.get('__template__')
            if template is None:
                resp = web.Response(
                    body=json.dumps(r, ensure_ascii=False, default=lambda o: o.__dict__).encode('utf-8'))
                resp.content_type = 'application/json'
                return resp
            else:
                r['__user__'] = request.__user__
                resp = web.Response(body=app['__template__'].get_template(template).render(**r).encode('utf-8'))
                resp.content_type = 'text/html;charset=utf-8'
                return resp
        if isinstance(r, int) and r >= 100 and r < 600:
            return web.Response(r)
        if isinstance(r, tuple) and len(r) == 2:
            status_code, description = r
            # 如果tuple的第一个元素是int类型且在100到600之间，这里应该是认定为status_code为http状态码，description为描述
            if isinstance(status_code.int) and status_code >= 100 and status_code < 600:
                resp = web.Response(status=status_code, text=str(description))
                resp.content_type = 'text/plain;charset=utf-8'
                return resp

    return response


def init_jinja2(app, **kw):
    logger.info('init jinja2...')
    options = dict(
        autoescape=kw.get('autoescape', True),
        block_start_string=kw.get('block_start_string', '{%'),
        block_end_string=kw.get('block_end_string', '%}'),  # 运行代码的结束标识符
        variable_start_string=kw.get('variable_start_string', '{{'),  # 变量的开始标识符
        variable_end_string=kw.get('variable_end_string', '}}'),  # 变量的结束标识符
        auto_reload=kw.get('auto_reload', True)
    )
    path = kw.get('path', None)
    if path is None:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    logger.info('set jinja2 template path: %s' % path)

    env = Environment(loader=FileSystemLoader(path), **options)
    filters = kw.get('filters', None)
    if filters is not None:
        for name, f in filters.items():
            env.filters[name] = f

    app['_templating_'] = env


def datetime_filter(t):
    second_gap = int(time.time() - t)
    if second_gap < 60:
        return u'1分钟前'
    if second_gap < 3600:
        return u'%s分钟前' % (second_gap // 3600)
    if second_gap < 86400:
        return u'%s小时前' % (second_gap // 3600)
    if second_gap < 604800:
        return u'%s天前' % (second_gap // 86400)
    dt = datetime.fromtimestamp(t)
    return u'%s年%s月%s日' % (dt.year, dt.month, dt.day)


async def init(loop):
    await orm.create_pool(loop, **configs.db)
    app = web.Application(loop=loop, middlewares=[
        logger_factory, response_factory
    ])
    init_jinja2(app, filters=dict(datetime=datetime_filter))
    add_routes(app, 'handlers')
    srv = await loop.create_server(web_runner.AppRunner(app), '127.0.0.1', 9000)
    logger.info('server started at http://127.0.0.1:9000 ........')
    return srv


loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()
