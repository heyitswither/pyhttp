#!/bin/env python3
import argparse
import platform
import socket

"""
# TODO
- support gzip
- probably more
"""

REQ = "{method} {path} HTTP/1.1\r\nHost: {host}:{port}\r\nConnection: close\r\n{headers}\r\n{data}\r\n"

METHODS = ['GET', 'POST', 'HEAD', 'PUT', 'DELETE', 'OPTIONS', 'CONNECT', 'TRACE']
__version__ = "1.0.1"
HEADERS = {"User-agent": f"pyhttp/{__version__}", "Accept-Encoding": "deflate", "Accept": "*/*"}


def stripheaders(da: str, header_only: bool =False) -> [tuple, str]:
    header = da.split('\r\n\r\n', 1)[0]
    data = da.split('\r\n\r\n', 1)[1]
    if header_only:
        return header
    return header, data


def hdict2str(dic: dict) -> str:
    ret = ""
    for key, value in dic.items():
        ret += key.title() + ": " + value + "\r\n"
    return ret


def str2hdict(st: str) -> dict:
    ret = {}
    for line in st.splitlines():
        if line.startswith('HTTP'):
            ret['code'] = [int(s) for s in line.split() if s.isdigit()][0]
            continue
        ret[line.split(': ')[0]] = line.split(': ')[1].split('\r', 1)[0]
    return ret


def parse_url(url: str) -> tuple:
    if not url.startswith('http://'):
        raise ValueError('URL must start with http://')
    scheme, _, host = url.split('/', 2)
    if '/' in host:
        path = '/' + host.split('/', 1)[1]
    else:
        path = '/'
    host = host.split('/')[0]
    port = host.split(':')[1] if ':' in host else '80'
    host = host.split(':')[0] if ':' in host else host
    return scheme, host, int(port), path


def handle_headers(arg: argparse.Namespace) -> None:
    global HEADERS
    if arg.no_default_headers:
        HEADERS = {}
    if arg.headers:
        for i in arg.headers:
            HEADERS[i.split(':')[0]] = i.split(':')[1]


def read(so: socket.socket) -> str:
    ret = ""
    pdata = so.recv(1024)
    while pdata:
        try:
            ret += pdata.decode()
        except UnicodeDecodeError:
            pass
        pdata = so.recv(1024)
    return ret


def request(host: str, port: int, path: str, headers: dict, method: str, data: str) -> tuple:
    if data:
        headers['Content-Type'] = 'text/plain'
        headers['Content-Length'] = str(len(data))
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    s.sendall(REQ.format(method=method, path=path, host=host,
                         headers=hdict2str(headers), data=data,
                         port=port).encode())
    rdata = read(s)
    s.close()
    return stripheaders(rdata)


def main(arg):
    scheme, host, port, path = parse_url(arg.url)
    if arg.method is None:
        arg.method = "GET"
    if not arg.method.upper() in METHODS:
        print("WARN: unrecognised method: {}, continuing anyways...".format(arg.method.upper()))
    handle_headers(arg)
    reqh, reqd = request(host, port, path, HEADERS, arg.method.upper(), arg.data)
    print(reqd)
    if arg.verbose:
        print(str2hdict(reqh))


if __name__ == "__main__":
    parser = argparse.ArgumentParser("pyhttp", description="a non-interactive network retriever, written in Python")
    parser.version = "pyhttp {} ({})".format(__version__, platform.platform())
    parser.add_argument('url', help="URL to work with")
    parser.add_argument('-V', '--verbose', help="Make the operation more talkative", action="store_true")
    parser.add_argument('-v', '--version', help="Show the version number and quit", action="version")
    parser.add_argument('-M', '--method', help="Method used for HTTP request")
    parser.add_argument('-D', '--data', help="Data to send in request", default="")
    parser.add_argument('-H', '--headers', help="Send custom headers", default=[], nargs='*')
    parser.add_argument('--no-default-headers', help="Only send custom headers", action="store_true")
    args = parser.parse_args()
    main(args)
