import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / ".typing_data"
RECORDS_FILE = DATA_DIR / "records.json"
CUSTOM_TEXT_FILE = DATA_DIR / "custom_texts.json"

COLOR_CORRECT = 1
COLOR_WRONG = 2
COLOR_CURSOR = 3
COLOR_PENDING = 4
COLOR_HIGHLIGHT = 5
COLOR_MENU = 6

DIFFICULTY_LEVELS = {
    1: "入门",
    2: "初级",
    3: "中级",
    4: "进阶",
    5: "高级",
    6: "专家"
}


def ensure_data_dir():
    if not DATA_DIR.exists():
        DATA_DIR.mkdir(parents=True, exist_ok=True)
