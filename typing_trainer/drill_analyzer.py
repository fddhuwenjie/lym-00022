import random
from typing import List, Tuple, Dict, Optional
from collections import defaultdict

from .storage import Storage, HistoryAnalysis, DrillHistory
from .config import MIN_HISTORY_FOR_DRILL, DRILL_MIN_CHARS
from .courses import (
    WORD_LIBRARY, COMMON_WORDS, SENTENCE_TEMPLATES,
    ADJECTIVES, VERBS, NOUNS, ADVERBS
)


class DrillAnalyzer:
    def __init__(self):
        self.analysis: Optional[HistoryAnalysis] = None
        self.weak_chars: List[str] = []
        self.weak_bigrams: List[str] = []
        self.last_drill: Optional[DrillHistory] = None

    def load_analysis(self) -> bool:
        self.analysis = Storage.get_history_analysis()
        if self.analysis.total_sessions < MIN_HISTORY_FOR_DRILL:
            return False

        self.weak_chars = self._identify_weak_chars(10)
        self.weak_bigrams = self._identify_weak_bigrams(5)
        self.last_drill = Storage.get_last_drill()
        return True

    def has_enough_history(self) -> bool:
        if self.analysis is None:
            self.analysis = Storage.get_history_analysis()
        return self.analysis.total_sessions >= MIN_HISTORY_FOR_DRILL

    def get_history_count(self) -> int:
        if self.analysis is None:
            self.analysis = Storage.get_history_analysis()
        return self.analysis.total_sessions

    def _identify_weak_chars(self, top_n: int = 10) -> List[str]:
        if not self.analysis:
            return []

        char_scores: Dict[str, float] = defaultdict(float)

        for char, error_count in self.analysis.char_error_counts.items():
            if char.isspace() or char in '\n\r\t':
                continue
            error_score = error_count * 2.0

            if char in self.analysis.char_avg_times:
                times = self.analysis.char_avg_times[char]
                if times:
                    avg_time = sum(times) / len(times)
                    if avg_time > 0.3:
                        time_score = (avg_time - 0.3) * 10
                        error_score += time_score

            char_scores[char] = error_score

        sorted_chars = sorted(char_scores.items(), key=lambda x: x[1], reverse=True)
        return [char for char, _ in sorted_chars[:top_n]]

    def _identify_weak_bigrams(self, top_n: int = 5) -> List[str]:
        if not self.analysis:
            return []

        bigram_scores: Dict[str, float] = defaultdict(float)

        for bigram, error_count in self.analysis.bigram_error_counts.items():
            if not bigram or len(bigram) != 2:
                continue
            if any(c.isspace() or c in '\n\r\t' for c in bigram):
                continue

            error_score = error_count * 3.0

            if bigram in self.analysis.bigram_avg_times:
                times = self.analysis.bigram_avg_times[bigram]
                if times:
                    avg_time = sum(times) / len(times)
                    if avg_time > 0.4:
                        time_score = (avg_time - 0.4) * 15
                        error_score += time_score

            bigram_scores[bigram] = error_score

        sorted_bigrams = sorted(bigram_scores.items(), key=lambda x: x[1], reverse=True)
        return [bigram for bigram, _ in sorted_bigrams[:top_n]]

    def _find_words_with_char(self, char: str) -> List[str]:
        words = []
        char_lower = char.lower()

        for bigram, bigram_words in WORD_LIBRARY.items():
            if char_lower in bigram:
                words.extend(bigram_words)

        for word in COMMON_WORDS:
            if char_lower in word.lower() and word not in words:
                words.append(word)

        return list(set(words))

    def _find_words_with_bigram(self, bigram: str) -> List[str]:
        bigram_lower = bigram.lower()
        words = []

        if bigram_lower in WORD_LIBRARY:
            words.extend(WORD_LIBRARY[bigram_lower])

        for word in COMMON_WORDS:
            if bigram_lower in word.lower() and word not in words:
                words.append(word)

        return list(set(words))

    def _generate_drill_words(self) -> List[str]:
        drill_words = []

        for char in self.weak_chars:
            words = self._find_words_with_char(char)
            if words:
                selected = random.sample(words, min(3, len(words)))
                drill_words.extend(selected)

        for bigram in self.weak_bigrams:
            words = self._find_words_with_bigram(bigram)
            if words:
                selected = random.sample(words, min(4, len(words)))
                drill_words.extend(selected)

        random.shuffle(drill_words)
        return list(dict.fromkeys(drill_words))

    def _generate_sentence(self) -> str:
        template = random.choice(SENTENCE_TEMPLATES)
        num_placeholders = template.count('{}')

        fillers = []
        for i in range(num_placeholders):
            word_type = random.choice(['adj', 'verb', 'noun', 'adv', 'noun'])
            if word_type == 'adj':
                fillers.append(random.choice(ADJECTIVES))
            elif word_type == 'verb':
                fillers.append(random.choice(VERBS))
            elif word_type == 'noun':
                fillers.append(random.choice(NOUNS))
            else:
                fillers.append(random.choice(ADVERBS))

        return template.format(*fillers)

    def _generate_word_phrase(self, words: List[str]) -> str:
        if len(words) < 3:
            return ' '.join(words)

        phrase_parts = []
        i = 0
        while i < len(words):
            group_size = random.randint(2, 4)
            group = words[i:i + group_size]
            if random.random() < 0.3:
                adj = random.choice(ADJECTIVES)
                phrase_parts.append(f"{adj} {' '.join(group)}")
            else:
                phrase_parts.append(' '.join(group))
            i += group_size

        return ', '.join(phrase_parts)

    def generate_drill_text(self) -> str:
        if not self.has_enough_history():
            return ""

        drill_words = self._generate_drill_words()

        text_parts = []
        current_length = 0

        word_idx = 0
        while current_length < DRILL_MIN_CHARS:
            if word_idx < len(drill_words) - 5 and random.random() < 0.6:
                group = drill_words[word_idx:word_idx + random.randint(3, 6)]
                word_idx += len(group)
                phrase = self._generate_word_phrase(group)
                text_parts.append(phrase.capitalize() + '.')
                current_length += len(phrase) + 2
            else:
                sentence = self._generate_sentence()
                text_parts.append(sentence)
                current_length += len(sentence) + 1

            if current_length < DRILL_MIN_CHARS and random.random() < 0.4 and word_idx < len(drill_words):
                focus_words = drill_words[word_idx:word_idx + min(5, len(drill_words) - word_idx)]
                word_idx += len(focus_words)
                focus_text = "Practice these: " + ", ".join(focus_words) + "."
                text_parts.append(focus_text)
                current_length += len(focus_text) + 1

        final_text = ' '.join(text_parts)

        if len(final_text) < DRILL_MIN_CHARS:
            while len(final_text) < DRILL_MIN_CHARS:
                sentence = self._generate_sentence()
                final_text += ' ' + sentence

        return final_text[:1500]

    def compare_with_last_drill(self, current_wpm: float, current_accuracy: float,
                                current_rhythm: float) -> Dict:
        if not self.last_drill:
            return {
                'has_previous': False,
                'wpm_change': 0,
                'accuracy_change': 0,
                'rhythm_change': 0,
                'previous_wpm': 0,
                'previous_accuracy': 0,
                'previous_rhythm': 0
            }

        return {
            'has_previous': True,
            'wpm_change': current_wpm - self.last_drill.wpm,
            'accuracy_change': current_accuracy - self.last_drill.accuracy,
            'rhythm_change': current_rhythm - self.last_drill.rhythm_score,
            'previous_wpm': self.last_drill.wpm,
            'previous_accuracy': self.last_drill.accuracy,
            'previous_rhythm': self.last_drill.rhythm_score
        }

    def get_weakness_summary(self) -> str:
        if not self.weak_chars and not self.weak_bigrams:
            return "No weakness data available."

        parts = []

        if self.weak_chars:
            display_chars = [repr(c).strip("'") for c in self.weak_chars]
            parts.append(f"薄弱字符: {', '.join(display_chars)}")

        if self.weak_bigrams:
            parts.append(f"薄弱双字母: {', '.join(self.weak_bigrams)}")

        return " | ".join(parts)

    def get_comparison_bars(self, comparison: Dict) -> List[str]:
        if not comparison['has_previous']:
            return ["这是您的第一次专项训练！"]

        lines = []
        lines.append("=== 与上次专项训练对比 ===")
        lines.append("")

        metrics = [
            ("WPM", comparison['previous_wpm'], comparison['wpm_change']),
            ("准确率(%)", comparison['previous_accuracy'], comparison['accuracy_change']),
            ("节奏评分", comparison['previous_rhythm'], comparison['rhythm_change'])
        ]

        max_label_len = max(len(label) for label, _, _ in metrics)
        max_bar_width = 30

        for label, prev, change in metrics:
            current = prev + change
            max_val = max(prev, current, 1)

            prev_width = int((prev / max_val) * max_bar_width) if max_val > 0 else 0
            curr_width = int((current / max_val) * max_bar_width) if max_val > 0 else 0

            prev_bar = '█' * prev_width + '░' * (max_bar_width - prev_width)
            curr_bar = '█' * curr_width + '░' * (max_bar_width - curr_width)

            change_sign = '+' if change >= 0 else ''
            lines.append(f"{label.rjust(max_label_len)}:")
            lines.append(f"  上次: {prev_bar} {prev:.1f}")
            lines.append(f"  本次: {curr_bar} {current:.1f} ({change_sign}{change:.1f})")
            lines.append("")

        return lines
