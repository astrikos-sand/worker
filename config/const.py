from os import getenv as env
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

DEBUG = bool(int(env("DEBUG", 1)))
HOST = env("HOST", "0.0.0.0")
PORT = env("PORT", 5000)
DOCKER_SOCKET_PATH = env("DOCKER_SOCKET_PATH", "unix:///var/run/docker.sock")
BASE_DIR = Path(__file__).resolve().parent.parent
BACKEND_URL = env("BACKEND_URL")
TB_BACKEND_URL = env("TB_BACKEND_URL")
TBQ_HOST = env("TBQ_HOST")
LOCAL_IP = env("LOCAL_IP")
