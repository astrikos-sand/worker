from os import getenv as env
from distutils.util import strtobool
from pathlib import Path

DEBUG = bool(strtobool(env("DEBUG", "False")))
BACKEND_URL = env("BACKEND_URL", "http://backend:8000")
HOST = env("HOST", "0.0.0.0")
PORT = env("PORT", 5000)
DOCKER_SOCKET_PATH = env("DOCKER_SOCKET_PATH", "unix:///var/run/docker.sock")
BASE_DIR = Path(__file__).resolve().parent.parent
