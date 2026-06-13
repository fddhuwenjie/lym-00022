import time
import math
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
from collections import defaultdict


@dataclass
class TypingStats:
    total_chars: int = 0
    correct_chars: int = 0
    wrong_chars: int = 0
    start_time: float = 0
    end_time: float = 0
    error_distribution: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    keystroke_timings: List[Tuple[str, float]] = field(default_factory=list)
    pause_hotspots: List[Tuple[int, float]] = field(default_factory=list)
    bigram_timings: Dict[str, List[float]] = field(default_factory=lambda: defaultdict(list))
    bigram_errors: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    inter_keystroke_intervals: List[float] = field(default_factory=list)
    last_char: Optional[str] = None
    rhythm_score: float = 0.0
    section_stdevs: List[Tuple[int, float]] = field(default_factory=list)
    is_drill: bool = False
    drill_weak_chars: List[str] = field(default_factory=list)
    drill_weak_bigrams: List[str] = field(default_factory=list)

    def start(self):
        self.start_time = time.time()

    def end(self):
        self.end_time = time.time()

    @property
    def elapsed_time(self) -> float:
        if self.start_time == 0:
            return 0
        if self.end_time == 0:
            return time.time() - self.start_time
        return self.end_time - self.start_time

    @property
    def accuracy(self) -> float:
        if self.total_chars == 0:
            return 0.0
        return (self.correct_chars / self.total_chars) * 100

    @property
    def wpm(self) -> float:
        if self.elapsed_time == 0:
            return 0.0
        words = self.correct_chars / 5
        minutes = self.elapsed_time / 60
        return words / minutes if minutes > 0 else 0

    def record_correct(self, char: str, time_since_last: float):
        self.total_chars += 1
        self.correct_chars += 1
        self.keystroke_timings.append((char, time_since_last))
        if time_since_last > 0 and self.total_chars > 1:
            self.inter_keystroke_intervals.append(time_since_last)
        if time_since_last > 0.5:
            self.pause_hotspots.append((self.total_chars, time_since_last))
        if self.last_char is not None and char is not None:
            bigram = self.last_char + char
            self.bigram_timings[bigram].append(time_since_last)
        self.last_char = char

    def record_wrong(self, char: str, expected: str, time_since_last: float):
        self.total_chars += 1
        self.wrong_chars += 1
        self.error_distribution[expected] += 1
        self.keystroke_timings.append((char, time_since_last))
        if time_since_last > 0 and self.total_chars > 1:
            self.inter_keystroke_intervals.append(time_since_last)
        if self.last_char is not None and expected is not None:
            bigram = self.last_char + expected
            self.bigram_errors[bigram] += 1
        self.last_char = expected

    def top_errors(self, n: int = 5) -> List[Tuple[str, int]]:
        sorted_errors = sorted(self.error_distribution.items(), key=lambda x: x[1], reverse=True)
        return sorted_errors[:n]

    def slowest_chars(self, n: int = 5) -> List[Tuple[str, float]]:
        char_avg_times: Dict[str, List[float]] = defaultdict(list)
        for char, timing in self.keystroke_timings:
            char_avg_times[char].append(timing)
        
        result = []
        for char, timings in char_avg_times.items():
            if len(timings) >= 2:
                avg = sum(timings) / len(timings)
                result.append((char, avg))
        
        result.sort(key=lambda x: x[1], reverse=True)
        return result[:n]

    def calculate_rhythm_score(self) -> float:
        if len(self.inter_keystroke_intervals) < 5:
            self.rhythm_score = 0.0
            return 0.0
        
        intervals = self.inter_keystroke_intervals
        
        mean = sum(intervals) / len(intervals)
        variance = sum((x - mean) ** 2 for x in intervals) / len(intervals)
        std_dev = math.sqrt(variance)
        
        cv = std_dev / mean if mean > 0 else 1.0
        
        score = max(0.0, 100.0 - (cv * 150))
        score = min(100.0, score)
        
        self.rhythm_score = score
        return score

    def calculate_section_stdevs(self, section_size: int = 20) -> List[Tuple[int, float]]:
        if len(self.inter_keystroke_intervals) < section_size:
            self.section_stdevs = []
            return []
        
        intervals = self.inter_keystroke_intervals
        sections = []
        
        for i in range(0, len(intervals), section_size):
            section = intervals[i:i + section_size]
            if len(section) >= 5:
                mean = sum(section) / len(section)
                variance = sum((x - mean) ** 2 for x in section) / len(section)
                std_dev = math.sqrt(variance)
                sections.append((i // section_size, std_dev))
        
        self.section_stdevs = sections
        return sections

    def top_bigram_errors(self, n: int = 5) -> List[Tuple[str, int]]:
        sorted_bigrams = sorted(self.bigram_errors.items(), key=lambda x: x[1], reverse=True)
        return sorted_bigrams[:n]

    def slowest_bigrams(self, n: int = 5) -> List[Tuple[str, float]]:
        result = []
        for bigram, timings in self.bigram_timings.items():
            if len(timings) >= 2:
                avg = sum(timings) / len(timings)
                result.append((bigram, avg))
        
        result.sort(key=lambda x: x[1], reverse=True)
        return result[:n]
