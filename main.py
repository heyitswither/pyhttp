#!/bin/env python3
import argparse
import platform
import socket
import ssl
import base64
import json

from errors import *

context = ssl.SSLContext(ssl.PROTOCOL_TLS)

__version__ = "2.0.0"
REQ = "{method} {path} HTTP/1.1\r\nHost: {host}:{port}\r\nConnection: close\r\n{headers}\r\n{data}\r\n"
SCHEMES = ['http:', 'https:']
METHODS = ['GET', 'POST', 'HEAD', 'PUT', 'DELETE', 'OPTIONS', 'CONNECT', 'TRACE']
HEADERS = {'User-Agent': f'pyhttp/{__version__}', 'Allow': '*/*'}


def stripheaders(da: str) -> [tuple, str]:
    header = da.split('\r\n\r\n', 1)[0]
    try:
        data = da.split('\r\n\r\n', 1)[1]
    except:
        data = "Unsupported Content-Encoding"
    return header, data


def hdict2str(dic: dict) -> str:
    return ''.join('{}:{}\r\n'.format(k.title(), v) for k, v in dic.items())


def str2hdict(st: str) -> dict:
    ret = {}
    for line in st.splitlines():
        if line.startswith('HTTP'):
            ret['code'] = [int(s) for s in line.split() if s.isdigit()][0]
            ret['status'] = line.strip('HTTP/1.1')[1:]
            continue
        ret[line.split(': ')[0]] = line.split(': ')[1].split('\r', 1)[0]
    return ret


def parse_url(url: str) -> tuple:
    try:
        scheme, _, host = url.split('/', 2)
    except ValueError:
        raise InvalidURI(url)

    if '/' in host:
        path = '/' + host.split('/', 1)[1]
    else:
        path = '/'
    host = host.split('/')[0]
    port = int(host.split(':')[1]) if ':' in host else 80 if scheme == 'http:' else 443 if scheme == 'https:' else 0
    host = host.split(':')[0] if ':' in host else host
    return scheme, host, int(port), path


def handle_headers(arg: argparse.Namespace) -> None:
    global HEADERS
    if arg.no_default_headers:
        HEADERS = {}
    if arg.headers:
        for i in arg.headers:
            HEADERS[i.split(':')[0]] = i.split(':')[1]
    if arg.auth:
        HEADERS['Authorization'] = (arg.auth.split('/')[0].encode() + " ".encode() + base64.encodestring(arg.auth.split('/')[1].encode()).strip()).decode()


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


def request(host: str, port: int, path: str, headers: dict, method: str, data: str, scheme: str) -> tuple:
    if data:
        headers['Content-Type'] = 'text/plain'
        headers['Content-Length'] = str(len(data))
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if scheme == 'https:':
        s = context.wrap_socket(s, server_hostname=host)

    s.connect((host, port))
    s.sendall(REQ.format(method=method, path=path, host=host,
                         headers=hdict2str(headers), data=data,
                         port=port).encode())
    rdata = read(s)
    s.close()
    return stripheaders(rdata)

def main(args):
    while True:
        scheme, host, port, path = parse_url(args.url)
        if not scheme in SCHEMES:
            raise InvalidScheme(f"Scheme {scheme} is not supported")
        if args.method is None:
            args.method = "GET"
        if not args.method.upper() in METHODS:
            print("WARN: unrecognised method: {}, continuing anyways...".format(args.method.upper()))
        handle_headers(args)
        reqh, reqd = request(host, port, path, HEADERS, args.method.upper(), args.data, scheme)
        headers = str2hdict(reqh)
        if args.verbose and args.markers:
            print("-------BEGIN HEADERS-------")
        if args.verbose and not args.json:
            print(reqh)
        if args.verbose and args.json:
            print(json.dumps(headers))
        if args.verbose and args.markers:
            print("--------END HEADERS--------")
        if not (args.verbose and args.no_data):
            if args.verbose and args.markers:
                print("-------BEGIN DATA-------")
            print(reqd[:-1])
            if args.verbose and args.markers:
                print("--------END DATA--------")
        try:
            if headers['code'] >= 400 or headers['code'] < 300 or args.no_redirect:
                break
        except KeyError:
            break
        print(f"Redirecting [{headers['status']}] {args.url} => {headers['Location']}")
        args.url = headers['Location']

if __name__ == "__main__":
    parser = argparse.ArgumentParser("pyhttp", description="a non-interactive network retriever, written in Python")
    parser.version = "pyhttp {} ({})".format(__version__, platform.platform())
    parser.add_argument('url', help="URL to work with")
    parser.add_argument('-V', '--verbose', help="Make the operation more talkative", action="store_true")
    parser.add_argument('-j', '--json', help="Headers as JSON (-V)", action="store_true")
    parser.add_argument('-n', '--no-data', help="Don't print data (-V)", action="store_true")
    parser.add_argument('-m', '--markers', help="Add markers to the output (-V)", action="store_true")
    parser.add_argument('-v', '--version', help="Show the version number and quit", action="version")
    parser.add_argument('-M', '--method', help="Method used for HTTP request")
    parser.add_argument('-D', '--data', help="Data to send in request", default="")
    parser.add_argument('-H', '--headers', help="Send custom headers", default=[], nargs='*')
    parser.add_argument('-R', '--no-redirect', help="Don't allow redirects", action="store_true")
    parser.add_argument('-A', '--auth', help="Authenticate with the server(Type/User:Pass)")
    parser.add_argument('--no-default-headers', help="Only send custom headers", action="store_true")
    args = parser.parse_args()
    main(args)
