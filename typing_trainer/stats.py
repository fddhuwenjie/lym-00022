import time
from dataclasses import dataclass, field
from typing import Dict, List, Tuple
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
        if time_since_last > 0.5:
            self.pause_hotspots.append((self.total_chars, time_since_last))

    def record_wrong(self, char: str, expected: str, time_since_last: float):
        self.total_chars += 1
        self.wrong_chars += 1
        self.error_distribution[expected] += 1
        self.keystroke_timings.append((char, time_since_last))

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
