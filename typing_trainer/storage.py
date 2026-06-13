import json
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
from dataclasses import dataclass, asdict, field
from collections import defaultdict
from .config import (
    RECORDS_FILE, CUSTOM_TEXT_FILE, RHYTHM_HISTORY_FILE,
    DRILL_HISTORY_FILE, HISTORY_ANALYSIS_FILE, ensure_data_dir
)


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
    rhythm_score: float = 0.0
    is_drill: bool = False
    drill_weak_chars: List[str] = field(default_factory=list)
    drill_weak_bigrams: List[str] = field(default_factory=list)
    error_distribution: Dict[str, int] = field(default_factory=dict)
    bigram_errors: Dict[str, int] = field(default_factory=dict)
    keystroke_avg_times: Dict[str, float] = field(default_factory=dict)
    bigram_avg_times: Dict[str, float] = field(default_factory=dict)


@dataclass
class DrillHistory:
    id: int
    timestamp: str
    weak_chars: List[str]
    weak_bigrams: List[str]
    wpm: float
    accuracy: float
    rhythm_score: float


@dataclass
class HistoryAnalysis:
    total_sessions: int
    char_error_counts: Dict[str, int]
    bigram_error_counts: Dict[str, int]
    char_avg_times: Dict[str, List[float]]
    bigram_avg_times: Dict[str, List[float]]
    last_updated: str


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
        is_custom: bool = False,
        is_drill: bool = False
    ) -> Record:
        records = Storage._load_records()
        new_id = max([r['id'] for r in records], default=0) + 1
        
        char_avg_times = {}
        for char, timing in stats.keystroke_timings:
            if char not in char_avg_times:
                char_avg_times[char] = []
            char_avg_times[char].append(timing)
        keystroke_avg_times = {
            char: sum(timings) / len(timings) 
            for char, timings in char_avg_times.items() if len(timings) >= 1
        }
        
        bigram_avg_times = {
            bigram: sum(timings) / len(timings)
            for bigram, timings in stats.bigram_timings.items() if len(timings) >= 1
        }
        
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
            is_custom=is_custom,
            rhythm_score=stats.rhythm_score,
            is_drill=is_drill,
            drill_weak_chars=list(stats.drill_weak_chars),
            drill_weak_bigrams=list(stats.drill_weak_bigrams),
            error_distribution=dict(stats.error_distribution),
            bigram_errors=dict(stats.bigram_errors),
            keystroke_avg_times=keystroke_avg_times,
            bigram_avg_times=bigram_avg_times
        )

    @staticmethod
    def _load_rhythm_history() -> List[Dict]:
        ensure_data_dir()
        if not RHYTHM_HISTORY_FILE.exists():
            return []
        try:
            with open(RHYTHM_HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []

    @staticmethod
    def _save_rhythm_history(history: List[Dict]):
        ensure_data_dir()
        with open(RHYTHM_HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

    @staticmethod
    def add_rhythm_entry(record_id: int, rhythm_score: float, timestamp: str):
        history = Storage._load_rhythm_history()
        history.append({
            'record_id': record_id,
            'rhythm_score': rhythm_score,
            'timestamp': timestamp
        })
        if len(history) > 100:
            history = history[-100:]
        Storage._save_rhythm_history(history)

    @staticmethod
    def get_recent_rhythm(limit: int = 10) -> List[Dict]:
        history = Storage._load_rhythm_history()
        history.sort(key=lambda x: x['timestamp'], reverse=True)
        return history[:limit]

    @staticmethod
    def _load_drill_history() -> List[Dict]:
        ensure_data_dir()
        if not DRILL_HISTORY_FILE.exists():
            return []
        try:
            with open(DRILL_HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []

    @staticmethod
    def _save_drill_history(history: List[Dict]):
        ensure_data_dir()
        with open(DRILL_HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

    @staticmethod
    def add_drill_entry(
        weak_chars: List[str],
        weak_bigrams: List[str],
        wpm: float,
        accuracy: float,
        rhythm_score: float
    ) -> DrillHistory:
        history = Storage._load_drill_history()
        new_id = max([h['id'] for h in history], default=0) + 1
        entry = DrillHistory(
            id=new_id,
            timestamp=datetime.now().isoformat(),
            weak_chars=weak_chars,
            weak_bigrams=weak_bigrams,
            wpm=wpm,
            accuracy=accuracy,
            rhythm_score=rhythm_score
        )
        history.append(asdict(entry))
        Storage._save_drill_history(history)
        return entry

    @staticmethod
    def get_last_drill() -> Optional[DrillHistory]:
        history = Storage._load_drill_history()
        if not history:
            return None
        history.sort(key=lambda x: x['timestamp'], reverse=True)
        return DrillHistory(**history[0])

    @staticmethod
    def get_all_drill_history() -> List[DrillHistory]:
        history = Storage._load_drill_history()
        history.sort(key=lambda x: x['timestamp'])
        return [DrillHistory(**h) for h in history]

    @staticmethod
    def get_history_analysis() -> HistoryAnalysis:
        records = Storage.get_all_records()
        
        char_error_counts: Dict[str, int] = defaultdict(int)
        bigram_error_counts: Dict[str, int] = defaultdict(int)
        char_avg_times: Dict[str, List[float]] = defaultdict(list)
        bigram_avg_times: Dict[str, List[float]] = defaultdict(list)
        
        for record in records:
            for char, count in record.error_distribution.items():
                char_error_counts[char] += count
            for bigram, count in record.bigram_errors.items():
                bigram_error_counts[bigram] += count
            for char, avg_time in record.keystroke_avg_times.items():
                char_avg_times[char].append(avg_time)
            for bigram, avg_time in record.bigram_avg_times.items():
                bigram_avg_times[bigram].append(avg_time)
        
        return HistoryAnalysis(
            total_sessions=len(records),
            char_error_counts=dict(char_error_counts),
            bigram_error_counts=dict(bigram_error_counts),
            char_avg_times=dict(char_avg_times),
            bigram_avg_times=dict(bigram_avg_times),
            last_updated=datetime.now().isoformat()
        )

    @staticmethod
    def add_record(record: Record):
        records = Storage._load_records()
        records.append(asdict(record))
        Storage._save_records(records)
        if record.rhythm_score > 0:
            Storage.add_rhythm_entry(record.id, record.rhythm_score, record.timestamp)
        if record.is_drill:
            Storage.add_drill_entry(
                list(record.drill_weak_chars),
                list(record.drill_weak_bigrams),
                record.wpm,
                record.accuracy,
                record.rhythm_score
            )
