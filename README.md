# async_http_proxy

A simple HTTP proxy ( no support for HTTPS yet). 

## How to run?

You can either

1. `docker-compose up` - It would run the proxy on your localhost on port 8080 in a container
2. `HTTP_PROXY_PORT=<port-of-your-choice> python3 proxy.py`

## How to test?

There is a small testsuite in tests.py, that tests for sanity of the proxy. You can run it
with the following commands.

1. `pip install -r test_requirements.txt`
2. `pytest tests.py`

## How to use it 

You can set the proxy at the application level eg. for your browser that allow for setting 
browser specific `HTTP_PROXY` (such as Firefox) or `$http_proxy` variable for commandline applications.

**At the moment, docker based proxy does not work if `HTTP_PROXY` is set at os level.** If you intent to 
set the `HTTP_PROXY` for the entire os I suggest running proxy as a python process on the host.
computer.

### Stats

Once the proxy is up and running, you can go to `http://localhost:8080/stats` to see the following information
as json

* uptime
* bytes transferred

## License
Released under Apache 2.0. Please see [License](License) to see full terms.

## Copyright

© 2019 Mohit Ranka
