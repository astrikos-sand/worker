from os import getenv as env
from distutils.util import strtobool

DEBUG = bool(strtobool(env("DEBUG", "False")))
BACKEND_URL = env("BACKEND_URL", "http://backend:8000")
HOST = env("HOST", "0.0.0.0")
PORT = env("PORT", 5000)
