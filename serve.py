#!/usr/bin/env python3
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse
from sim.atm_server import run_verilog_simulation

ROOT = Path(__file__).resolve().parent
STATIC_DIR = ROOT

class Handler(BaseHTTPRequestHandler):
    def _set_headers(self, code=200, content_type='text/html'):
        self.send_response(code)
        self.send_header('Content-Type', content_type)
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.lstrip('/') or 'index.html'
        file_path = STATIC_DIR / path
        if file_path.exists() and file_path.is_file():
            content_type = 'application/javascript' if file_path.suffix == '.js' else 'text/html'
            if file_path.suffix == '.css':
                content_type = 'text/css'
            elif file_path.suffix == '.json':
                content_type = 'application/json'
            self._set_headers(200, content_type)
            self.wfile.write(file_path.read_bytes())
            return
        self._set_headers(404, 'text/plain')
        self.wfile.write(b'Not Found')

    def do_POST(self):
        if self.path != '/api/run':
            self._set_headers(404, 'text/plain')
            self.wfile.write(b'Not Found')
            return
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length).decode('utf-8')
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            self._set_headers(400, 'application/json')
            self.wfile.write(json.dumps({'ok': False, 'error': 'Invalid JSON'}).encode())
            return
        result = run_verilog_simulation(data.get('actions', []))
        self._set_headers(200, 'application/json')
        self.wfile.write(json.dumps(result).encode('utf-8'))

if __name__ == '__main__':
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    server = HTTPServer(('0.0.0.0', port), Handler)
    print(f'Serving ATM demo on http://127.0.0.1:{port}')
    server.serve_forever()
