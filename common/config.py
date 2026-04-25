from os import getenv

from dotenv import load_dotenv

load_dotenv()


def _required(name: str) -> str:
    value = getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


DB_USERNAME = _required("DB_USERNAME")
DB_PASSWORD = _required("DB_PASSWORD")
DB_SERVER = _required("DB_SERVER")
DB_DATABASE = _required("DB_DATABASE")

SB_SEND_CONNECTION_STRING = getenv("SB_SEND_CONNECTION_STRING", "")
SB_LISTEN_CONNECTION_STRING = getenv("SB_LISTEN_CONNECTION_STRING", "")
SB_QUEUE_NAME = getenv("SB_QUEUE_NAME", "alekseikarpukovich")
FEEDBACK_WORKER_INTERVAL_SECONDS = int(getenv("FEEDBACK_WORKER_INTERVAL_SECONDS", "10"))