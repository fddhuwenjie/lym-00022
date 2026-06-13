import json
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
from dataclasses import dataclass, asdict
from .config import RECORDS_FILE, CUSTOM_TEXT_FILE, ensure_data_dir


@dataclass
class Record:
    id: int
    course_id: Optional[int]
    course_name: str
    wpm: float
    accuracy: float
    total_chars: int
    correct_chars: int
    wrong_chars: int
    duration: float
    timestamp: str
    blind_mode: bool = False
    time_limit: Optional[int] = None
    is_custom: bool = False


@dataclass
class CustomText:
    id: int
    name: str
    content: str
    created_at: str


class Storage:
    @staticmethod
    def _load_records() -> List[Dict]:
        ensure_data_dir()
        if not RECORDS_FILE.exists():
            return []
        try:
            with open(RECORDS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []

    @staticmethod
    def _save_records(records: List[Dict]):
        ensure_data_dir()
        with open(RECORDS_FILE, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)

    @staticmethod
    def add_record(record: Record):
        records = Storage._load_records()
        records.append(asdict(record))
        Storage._save_records(records)

    @staticmethod
    def get_all_records() -> List[Record]:
        data = Storage._load_records()
        return [Record(**item) for item in data]

    @staticmethod
    def get_records_by_course(course_id: int) -> List[Record]:
        all_records = Storage.get_all_records()
        return [r for r in all_records if r.course_id == course_id]

    @staticmethod
    def get_recent_records(limit: int = 20) -> List[Record]:
        records = Storage.get_all_records()
        records.sort(key=lambda r: r.timestamp, reverse=True)
        return records[:limit]

    @staticmethod
    def get_best_wpm(course_id: Optional[int] = None) -> Optional[Record]:
        records = Storage.get_all_records()
        if course_id is not None:
            records = [r for r in records if r.course_id == course_id]
        if not records:
            return None
        return max(records, key=lambda r: r.wpm)

    @staticmethod
    def _load_custom_texts() -> List[Dict]:
        ensure_data_dir()
        if not CUSTOM_TEXT_FILE.exists():
            return []
        try:
            with open(CUSTOM_TEXT_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []

    @staticmethod
    def _save_custom_texts(texts: List[Dict]):
        ensure_data_dir()
        with open(CUSTOM_TEXT_FILE, 'w', encoding='utf-8') as f:
            json.dump(texts, f, ensure_ascii=False, indent=2)

    @staticmethod
    def add_custom_text(name: str, content: str) -> CustomText:
        texts = Storage._load_custom_texts()
        new_id = max([t['id'] for t in texts], default=0) + 1
        custom = CustomText(
            id=new_id,
            name=name,
            content=content,
            created_at=datetime.now().isoformat()
        )
        texts.append(asdict(custom))
        Storage._save_custom_texts(texts)
        return custom

    @staticmethod
    def get_all_custom_texts() -> List[CustomText]:
        data = Storage._load_custom_texts()
        return [CustomText(**item) for item in data]

    @staticmethod
    def delete_custom_text(text_id: int):
        texts = Storage._load_custom_texts()
        texts = [t for t in texts if t['id'] != text_id]
        Storage._save_custom_texts(texts)

    @staticmethod
    def create_record_from_stats(
        stats,
        course_id: Optional[int],
        course_name: str,
        blind_mode: bool = False,
        time_limit: Optional[int] = None,
        is_custom: bool = False
    ) -> Record:
        records = Storage._load_records()
        new_id = max([r['id'] for r in records], default=0) + 1
        
        return Record(
            id=new_id,
            course_id=course_id,
            course_name=course_name,
            wpm=stats.wpm,
            accuracy=stats.accuracy,
            total_chars=stats.total_chars,
            correct_chars=stats.correct_chars,
            wrong_chars=stats.wrong_chars,
            duration=stats.elapsed_time,
            timestamp=datetime.now().isoformat(),
            blind_mode=blind_mode,
            time_limit=time_limit,
            is_custom=is_custom
        )
