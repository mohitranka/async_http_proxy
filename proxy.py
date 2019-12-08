#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-

"""proxy.py A simple asynhronous http proxy"""

__author__      = 'Mohit Ranka'
__maintainer__  = 'Mohit Ranka'
__email__       = 'mohitranka@gmail.com'
__version__     = '0.1.0'

import asyncio
import io
import ipaddress
import json
import os
import socket
import time
import aiohttp.web
from aiohttp_requests import requests

# Constants
MAX_CHUNK_SIZE = 1024
HTTP_BAD_REQUEST = 400
HTTP_RANGE_NOT_SATISFIABLE = 416

# Variables 
content_length = 0
start_time = time.time()

                                        #####################
                                        # Private Functions #
                                        #####################

async def _is_loopback(req_host):
    host, port = req_host.split(":") 
    addr = socket.getaddrinfo(host, port)[-1][-1][0]
    ip = ipaddress.ip_address(addr)
    return ip.is_loopback

async def _get_request_response(method, url, headers):
    response = None
    if method in ('GET', 'POST', 'HEAD', 'DELETE', 'PUT', 'PATCH', 'CONNECT'):
        response = await getattr(requests, method.lower())(url, headers=headers)
    return response

async def _validate_and_enhance_request_headers(req):
    req_headers = dict(req.headers)
    req_headers['X-FORWARDED-FOR'] = req.remote or ''
    req_headers['X-FORWARDED-PROTO'] = 'http'
    query_range = req.query.get('range')
    header_range = req_headers.get('Range') or req_headers.get('range')
    if query_range:
        if header_range and header_range[6:].strip() != query_range:
            return req_headers, False
        req_headers['range'] = 'bytes=%s'%(query_range)
    elif not header_range: # Hack to handle requests that give partial response
        req_headers['range'] = 'bytes=0-'
    return req_headers, True

async def _get_stats(): 
    data = json.dumps({
        "uptime": time.time() - start_time,
        "bytes": content_length
        })
    return data.encode()


async def _create_proxy_response(response):
    if response is None:
        proxy_response = aiohttp.web.Response(status=HTTP_BAD_REQUEST)
    else:
        proxy_response = aiohttp.web.Response( status=response.status, headers=response.headers)
    return proxy_response


async def _prepare_proxy_response(proxy_response, response):
    if not response:
        return

    global content_length
    content_length += int(response.headers['Content-Length'])
    while True:
        chunk = await response.content.read(MAX_CHUNK_SIZE)
        if not chunk:
            break
        await proxy_response.write(chunk)
    await proxy_response.write_eof()

                                        ####################                 
                                        # Public Functions #
                                        ####################

async def handler( req):
    print("Processing the request for", req.url)
    if req.path == '/stats' and await _is_loopback(req.host):
        response = await process_stats_response(req)
    else:
        response = await process_proxy_response(req)
    return response

async def process_proxy_response( req ):
    """
    Method to handle the processing of the client http request to the 
    remote endpoint.
    """
    global content_length
    req_headers, is_valid = await _validate_and_enhance_request_headers(req)
    if not is_valid: 
        # Throw 416
        proxy_response = aiohttp.web.Response(status=HTTP_RANGE_NOT_SATISFIABLE)
        await proxy_response.prepare(req)
        await proxy_response.write_eof()
        return proxy_response
    else:
        response = await _get_request_response(req.method, req.url, req_headers)
        proxy_response = await _create_proxy_response(response)
        proxy_response.headers['Via'] = 'http/1.1 async http proxy'
        await proxy_response.prepare(req)
        await _prepare_proxy_response(proxy_response, response)
        return proxy_response

async def process_stats_response( req ):
    """
    Method to handle the processing of response of proxy stats
    from '/stats' endpoint
    """
    proxy_response = aiohttp.web.Response()
    data = await _get_stats()
    proxy_response.headers['Content-Length'] = str(len(data))
    proxy_response.headers['Content-Type'] = 'application/json'
    await proxy_response.prepare(req)
    await proxy_response.write(data)
    await proxy_response.write_eof()
    return proxy_response


async def main():
    server = aiohttp.web.Server(handler)
    runner = aiohttp.web.ServerRunner(server)
    await runner.setup()
    site = aiohttp.web.TCPSite(runner, '0.0.0.0', os.environ['HTTP_PROXY_PORT'])
    await site.start()
    print("Running http proxy on port", os.environ['HTTP_PROXY_PORT'])
    while True:
        await asyncio.sleep(1)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        server = loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("Terminating http proxy running on port",  os.environ['HTTP_PROXY_PORT'])
    loop.close()
