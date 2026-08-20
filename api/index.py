import os
import sys

# Setup root dan app path agar import modul dan data selalu ditemukan
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_DIR = os.path.join(ROOT_DIR, 'app')

for path in [ROOT_DIR, APP_DIR]:
    if path not in sys.path:
        sys.path.insert(0, path)

from app.app import app

# WSGI Middleware agar path tetap presisi saat di-rewrite oleh Vercel
class PrefixMiddleware:
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        path = environ.get('PATH_INFO', '')
        for prefix in ['/api/index', '/api']:
            if path.startswith(prefix):
                stripped = path[len(prefix):]
                environ['PATH_INFO'] = stripped if stripped else '/'
                break
        return self.wsgi_app(environ, start_response)

app.wsgi_app = PrefixMiddleware(app.wsgi_app)

# Vercel entrypoint
app = app
