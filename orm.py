#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2018/9/11 上午10:23
# @Author  : huangjie
# @Site    : 
# @File    : orm.py
# @Software: PyCharm

from logger import logger

import asyncio, aiomysql

__pool = None


def log(sql, args=()):
    logger.info('SQL: %s, ARGS: %s' % (sql, args))


async def create_pool(loop, **kw):
    logger.info('create database connection pool...')
    global __pool
    __pool = await aiomysql.create_pool(
        host=kw.get('host', 'localhost'),
        port=kw.get('port', '3306'),
        user=kw['user'],
        password=kw['password'],
        db=kw['database'],
        charset=kw.get('charset', 'utf8'),
        autocommit=kw.get('autocommit', True),
        maxsize=kw.get('maxsize', 10),
        minsize=kw.get('minsize', 1),
        loop=loop
    )


async def select(sql, args, size=None):
    log(sql, args)
    global __pool
    async with __pool.get() as conn:
        try:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(sql.replace('?', '%s'), args or ())
                if size:
                    rs = await cur.fetchmany(size)
                else:
                    rs = await cur.fetchall()
        except BaseException as e:
            rs = []
            logger.info(e)
        logger.info('rows returned: %s' % len(rs))
        return rs


async def execute(sql, args, autocommit=True):
    async with __pool.get() as conn:
        if not autocommit:
            await conn.begin()
        try:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(sql.replace('?', '%s'), args or ())
                affected = cur.rowcount
            if autocommit:
                await cur.commit()
                logger.info('commit success!')
        except BaseException as e:
            if not autocommit:
                await cur.rollback()
            raise
        return affected
