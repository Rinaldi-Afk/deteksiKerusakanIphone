import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_DIR = os.path.join(ROOT_DIR, 'app')

for path in [ROOT_DIR, APP_DIR]:
    if path not in sys.path:
        sys.path.insert(0, path)

from app.app import app

# Vercel entrypoint
app = app
