import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / ".typing_data"
RECORDS_FILE = DATA_DIR / "records.json"
CUSTOM_TEXT_FILE = DATA_DIR / "custom_texts.json"
RHYTHM_HISTORY_FILE = DATA_DIR / "rhythm_history.json"
DRILL_HISTORY_FILE = DATA_DIR / "drill_history.json"
HISTORY_ANALYSIS_FILE = DATA_DIR / "history_analysis.json"

COLOR_CORRECT = 1
COLOR_WRONG = 2
COLOR_CURSOR = 3
COLOR_PENDING = 4
COLOR_HIGHLIGHT = 5
COLOR_MENU = 6
COLOR_RED = 7
COLOR_BLUE = 8
COLOR_MAGENTA = 9

DIFFICULTY_LEVELS = {
    1: "入门",
    2: "初级",
    3: "中级",
    4: "进阶",
    5: "高级",
    6: "专家"
}

RHYTHM_PAUSE_THRESHOLD_MS = 500
RHYTHM_SECTION_SIZE = 20
MIN_HISTORY_FOR_DRILL = 5
DRILL_MIN_CHARS = 200
MAX_MULTIPLAYER_PLAYERS = 4
DEFAULT_MULTIPLAYER_PORT = 54321
MULTIPLAYER_COUNTDOWN_SECONDS = 3

NETWORK_TIMEOUT = 0.1
SERVER_POLL_INTERVAL = 0.05
CLIENT_POLL_INTERVAL = 0.05

MSG_TYPE_HELLO = "hello"
MSG_TYPE_LOBBY_UPDATE = "lobby_update"
MSG_TYPE_READY = "ready"
MSG_TYPE_COUNTDOWN = "countdown"
MSG_TYPE_START = "start"
MSG_TYPE_PROGRESS = "progress"
MSG_TYPE_FINISH = "finish"
MSG_TYPE_CHAT = "chat"
MSG_TYPE_DISCONNECT = "disconnect"


def ensure_data_dir():
    if not DATA_DIR.exists():
        DATA_DIR.mkdir(parents=True, exist_ok=True)
