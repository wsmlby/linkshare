#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from hashlib import sha256
import http.server
import sys
from urllib.parse import unquote, urlparse, parse_qs, quote
import os
import time


def file_permission_restrict_enough(file_path):
    return os.stat(file_path).st_mode & 0o777 == 0o600


def sign(path, key, exp):
    return sha256((path + key + "=" + str(exp)).encode()).hexdigest()


class LinkShareHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, key, base_path, *args):
        self.key = key
        http.server.SimpleHTTPRequestHandler.__init__(
            self, *args, directory=base_path)

    def validate_signature(self, sig, exp, path):
        if sign(path, self.key, exp) == sig:
            if exp == -1 or int(exp) > time.time():
                return True
            else:
                self.send_response(403)
                self.end_headers()
                self.wfile.write(b'Link Expired')
                return False
        self.send_response(403)
        self.end_headers()
        self.wfile.write(b'Forbidden bad signature')
        return False
        

    def do_GET(self):
        uri = urlparse(self.path)
        query = parse_qs(uri.query)
        if 'sig' not in query or len(query['sig']) < 1:
            self.send_response(403)
            self.end_headers()
            self.wfile.write(b'Forbidden: no signature')
            return
        path = unquote(uri.path)
        exp = -1
        exps = query.get('exp', [])
        if len(exps) > 0:
            exp = exps[0]
        if not self.validate_signature(query['sig'][0], exp, path):
            return
        self.path = path
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

if __name__ == "__main__":
    base_path = os.environ.get('LINKSHARE_BASE_PATH', '/share/')
    key = os.environ.get('LINKSHARE_KEY')
    if key is None:
        key_path = os.environ.get('LINKSHARE_KEY_PATH', '/etc/linkshare/key')
        if not os.path.exists(key_path):
            print('Key file not found')
            exit(-1)
        if not file_permission_restrict_enough(key_path):
            print('Key file permission not restrict enough: please use 600')
        with open(key_path, 'r') as f:
            key = f.read().strip()
        
    if key is None:
        print('Please set LINKSHARE_KEY or LINKSHARE_KEY_PATH')
        exit(-1)
    base_uri = os.environ.get('LINKSHARE_BASE_URI', 'http://localhost:8000')
    base_uri = base_uri.rstrip('/')

    if sys.argv[1] == 'share':
        file = sys.argv[2]
        file = os.path.abspath(file)
        base_path_stripped = os.path.abspath(base_path).rstrip('/')
        
        print(f"Sharing {file}")
        if not os.path.exists(file):
            print('File not found')
            exit(-1)
        
        if not file.startswith(base_path_stripped):
            print('File not in base path')
            exit(-1)
        file = file[len(base_path_stripped):]

        if len(sys.argv) > 3:
            exp = int(int(sys.argv[3]) + time.time())
        else:
            exp = -1
        
        sig = sign(file, key, exp)
        path0 = quote(file)
        new_path = f"{base_uri}{file}?sig={sig}" + \
            (f"&exp={exp}" if exp != -1 else "")
        print(new_path)
        exit(0)
    if sys.argv[1] == 'serve':
        def handler(*args):
            return LinkShareHttpRequestHandler(key, base_path, *args)
        PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 8000
        my_server = http.server.ThreadingHTTPServer(("", PORT), handler)
        import threading
        server_thread = threading.Thread(target=my_server.serve_forever)
        server_thread.start()
        print(f"Server started at port {PORT}")
        server_thread.join()
