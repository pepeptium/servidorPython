import sys
import os

# Ajusta el path si tu archivo está en una subcarpeta
path = '/home/pepeptium/servidorPython'
if path not in sys.path:
    sys.path.append(path)

from asgi import application  # importa desde asgi.py
