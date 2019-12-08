#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-

"""tests.py Unit tests for proxy.py"""

__author__      = 'Mohit Ranka'
__maintainer__  = 'Mohit Ranka'
__email__       = 'mohitranka@gmail.com'
__version__     = '0.1.0'

import asyncio
import pytest
from aiohttp import web
from aiohttp.test_utils import make_mocked_request 
import proxy

@pytest.mark.asyncio
async def test_stats():
    req = make_mocked_request("GET", "http://localhost:8080/stats", headers={'HOST': 'localhost:8080'})
    response = await proxy.handler(req)
    assert response.status == 200
    assert 40 <= int(response.headers['Content-Length']) <= 50
    assert response.headers['Content-Type'] == 'application/json'
    assert response.headers['Server'] == 'Python/3.8 aiohttp/3.6.2'

@pytest.mark.asyncio
async def test_incorrect_range_headers():
    req = make_mocked_request("GET", "http://www.example.com/?range=0-", headers={'HOST': 'example.com:80', 'range': 'bytes=1-'})
    response = await proxy.handler(req)
    assert response.status == 416
    assert response.headers['Content-Length'] == '0'
    assert response.headers['Content-Type'] == 'application/octet-stream'
    assert response.headers['Server'] == 'Python/3.8 aiohttp/3.6.2'

@pytest.mark.asyncio
async def test_example_com():
    req = make_mocked_request("GET", "http://www.example.com/", headers={'HOST': 'example.com:80'})
    response = await proxy.handler(req)
    assert response.status in (200, 206)
    assert response.headers['Via'] == 'http/1.1 async http proxy'
    assert response.headers['Accept-Ranges'] == 'bytes'
    assert response.headers['Content-Length'] == '1256'
    assert response.headers['Content-Type'] == 'text/html; charset=UTF-8'

@pytest.mark.asyncio
async def test_example_com_query_range():
    req = make_mocked_request("GET", "http://www.example.com/?range=100-", headers={'HOST': 'example.com:80'})
    response = await proxy.handler(req)
    assert response.status in (200, 206)
    assert response.headers['Via'] == 'http/1.1 async http proxy'
    assert response.headers['Accept-Ranges'] == 'bytes'
    assert response.headers['Content-Length'] == '1156'
    assert response.headers['Content-Type'] == 'text/html; charset=UTF-8'

@pytest.mark.asyncio
async def test_example_com_header_range():
    req = make_mocked_request("GET", "http://www.example.com/", headers={'HOST': 'example.com:80', 'range': 'bytes=100-'})
    response = await proxy.handler(req)
    assert response.status in (200, 206)
    assert response.headers['Via'] == 'http/1.1 async http proxy'
    assert response.headers['Accept-Ranges'] == 'bytes'
    assert response.headers['Content-Length'] == '1156'
    assert response.headers['Content-Type'] == 'text/html; charset=UTF-8'

@pytest.mark.asyncio
async def test_example_com_bad_request():
    req = make_mocked_request("BAD_HTTP_METHOD", "http://www.example.com/", headers={'HOST': 'example.com:80', 'range': 'bytes=100-'})
    response = await proxy.handler(req)
    assert response.status == 400
    assert response.headers['Via'] == 'http/1.1 async http proxy'
    assert response.headers['Content-Length'] == '0'
    assert response.headers['Content-Type'] == 'application/octet-stream'

