#!/usr/bin/env python3
"""Imagegen: AI image generator for the Pi. Generation runs free in your browser
via puter.js (no API key); this server hosts the page and saves images to disk."""
import base64, json, os, re, socket, sys, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

VERSION = '1.0.0'
HERE = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.environ.get('IMAGEGEN_DIR') or os.path.join(HERE, 'images')
MAX_IMAGE_BYTES = 25 * 1024 * 1024

def safe_name(name):
    slug = re.sub(r'[^a-z0-9]+', '-', (name or 'image').lower()).strip('-')[:40]
    return slug or 'image'

def save_image(prompt, b64, image_dir=None):
    """Decode + write a PNG for the prompt. Returns the relative path."""
    image_dir = image_dir or IMAGE_DIR
    raw = base64.b64decode(b64, validate=True)
    if not raw.startswith(b'\x89PNG'):
        raise ValueError('not a PNG')
    if len(raw) > MAX_IMAGE_BYTES:
        raise ValueError('image too large')
    os.makedirs(image_dir, exist_ok=True)
    path = os.path.join(image_dir, '%s-%s.png' % (time.strftime('%Y%m%d-%H%M%S'), safe_name(prompt)))
    with open(path, 'wb') as fh:
        fh.write(raw)
    return path

def list_images(image_dir=None):
    image_dir = image_dir or IMAGE_DIR
    try:
        return sorted(f for f in os.listdir(image_dir) if f.endswith('.png'))
    except OSError:
        return []

def free_port(preferred=8317):
    for port in (preferred, 0):
        with socket.socket() as s:
            try:
                s.bind(('127.0.0.1', port))
                return s.getsockname()[1]
            except OSError:
                continue
    raise RuntimeError('no free port')

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):  # keep the terminal clean
        pass
    def _json(self, obj, code=200):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    def do_GET(self):
        if self.path == '/' or self.path.startswith('/?'):
            with open(os.path.join(HERE, 'index.html'), 'rb') as fh:
                body = fh.read()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path == '/images':
            self._json({'images': list_images()})
        elif self.path.startswith('/images/'):
            name = os.path.basename(self.path[len('/images/'):])
            path = os.path.join(IMAGE_DIR, name)
            if name.endswith('.png') and os.path.isfile(path):
                with open(path, 'rb') as fh:
                    body = fh.read()
                self.send_response(200)
                self.send_header('Content-Type', 'image/png')
                self.send_header('Content-Length', str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            else:
                self._json({'error': 'not found'}, 404)
        else:
            self._json({'error': 'not found'}, 404)
    def do_POST(self):
        if self.path != '/save':
            return self._json({'error': 'not found'}, 404)
        try:
            length = int(self.headers.get('Content-Length') or 0)
            data = json.loads(self.rfile.read(min(length, MAX_IMAGE_BYTES * 2)).decode())
            path = save_image(data.get('prompt', ''), data['data'])
            self._json({'saved': os.path.basename(path)})
        except (ValueError, KeyError, TypeError) as exc:
            self._json({'error': 'could not save: %s' % exc}, 400)

def main():
    if '--version' in sys.argv:
        print(VERSION); return 0
    port = free_port()
    server = ThreadingHTTPServer(('127.0.0.1', port), Handler)
    url = 'http://localhost:%d/' % port
    print('Imagegen is ready.')
    print('Open this in the Pi browser: %s' % url)
    print('Images you save land in: %s' % IMAGE_DIR)
    print('Press Ctrl+C to stop.')
    try:
        import subprocess
        subprocess.Popen(['xdg-open', url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
