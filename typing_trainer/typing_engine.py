import curses
import time
from typing import Optional
from .stats import TypingStats
from .config import COLOR_CORRECT, COLOR_WRONG, COLOR_CURSOR, COLOR_PENDING, COLOR_HIGHLIGHT


class TypingEngine:
    def __init__(self, stdscr, text: str, blind_mode: bool = False, time_limit: Optional[int] = None):
        self.stdscr = stdscr
        self.text = text
        self.blind_mode = blind_mode
        self.time_limit = time_limit
        self.stats = TypingStats()
        self.current_pos = 0
        self.last_keystroke_time = 0
        self.started = False
        self.finished = False
        self.quit_early = False
        self._init_colors()

    def _init_colors(self):
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(COLOR_CORRECT, curses.COLOR_GREEN, -1)
        curses.init_pair(COLOR_WRONG, curses.COLOR_WHITE, curses.COLOR_RED)
        curses.init_pair(COLOR_CURSOR, curses.COLOR_BLACK, curses.COLOR_CYAN)
        curses.init_pair(COLOR_PENDING, curses.COLOR_WHITE, -1)
        curses.init_pair(COLOR_HIGHLIGHT, curses.COLOR_YELLOW, -1)

    def run(self) -> TypingStats:
        self.stdscr.clear()
        self.stdscr.nodelay(False)
        curses.curs_set(0)
        
        max_y, max_x = self.stdscr.getmaxyx()
        
        while not self.finished and not self.quit_early:
            self._render(max_y, max_x)
            
            if self.time_limit and self.started:
                elapsed = time.time() - self.stats.start_time
                if elapsed >= self.time_limit:
                    self.finished = True
                    self.stats.end_time = time.time()
                    break
            
            try:
                key = self.stdscr.getch()
            except KeyboardInterrupt:
                self.quit_early = True
                break
            
            if key == 27:
                self.quit_early = True
                break
            
            if key in (curses.KEY_RESIZE,):
                max_y, max_x = self.stdscr.getmaxyx()
                continue
            
            if key < 32 or key > 126:
                if key in (curses.KEY_BACKSPACE, 8, 127):
                    self._handle_backspace()
                continue
            
            char = chr(key)
            self._handle_keystroke(char)
        
        return self.stats

    def _handle_keystroke(self, char: str):
        if self.current_pos >= len(self.text):
            return
        
        if not self.started:
            self.started = True
            self.stats.start()
            self.last_keystroke_time = time.time()
            time_since_last = 0
        else:
            current_time = time.time()
            time_since_last = current_time - self.last_keystroke_time
            self.last_keystroke_time = current_time
        
        expected_char = self.text[self.current_pos]
        
        if char == expected_char:
            self.stats.record_correct(char, time_since_last)
            self.current_pos += 1
            
            if self.current_pos >= len(self.text):
                self.finished = True
                self.stats.end_time = time.time()
        else:
            self.stats.record_wrong(char, expected_char, time_since_last)

    def _handle_backspace(self):
        pass

    def _render(self, max_y: int, max_x: int):
        self.stdscr.clear()
        
        info_y = 1
        self._render_status(info_y, max_x)
        
        text_y = info_y + 3
        self._render_text(text_y, max_x, max_y - text_y - 2)
        
        hint_y = max_y - 1
        hint = "按 ESC 退出"
        self.stdscr.addstr(hint_y, 0, hint, curses.color_pair(COLOR_PENDING) | curses.A_DIM)
        
        self.stdscr.refresh()

    def _render_status(self, y: int, max_x: int):
        status = []
        
        if self.started:
            wpm = self.stats.wpm
            status.append(f"WPM: {wpm:5.1f}")
        else:
            status.append("WPM:  --.--")
        
        if self.stats.total_chars > 0:
            acc = self.stats.accuracy
            status.append(f"准确率: {acc:5.1f}%")
        else:
            status.append("准确率:  --.-%")
        
        status.append(f"进度: {self.current_pos}/{len(self.text)}")
        
        if self.time_limit and self.started:
            elapsed = time.time() - self.stats.start_time
            remaining = max(0, self.time_limit - elapsed)
            minutes = int(remaining // 60)
            seconds = int(remaining % 60)
            status.append(f"剩余时间: {minutes:02d}:{seconds:02d}")
        
        if self.blind_mode:
            status.append("【盲打模式】")
        
        status_line = "  |  ".join(status)
        if len(status_line) > max_x:
            status_line = status_line[:max_x - 3] + "..."
        
        self.stdscr.addstr(y, 0, status_line, curses.color_pair(COLOR_HIGHLIGHT) | curses.A_BOLD)

    def _render_text(self, start_y: int, max_x: int, max_lines: int):
        text = self.text
        pos = 0
        line_num = 0
        
        while pos < len(text) and line_num < max_lines:
            line_end = min(pos + max_x, len(text))
            line = text[pos:line_end]
            
            x = 0
            for i, char in enumerate(line):
                abs_pos = pos + i
                
                if abs_pos < self.current_pos:
                    if self.blind_mode:
                        display_char = ' '
                    else:
                        display_char = char if char != '\n' else ' '
                    color = curses.color_pair(COLOR_CORRECT)
                elif abs_pos == self.current_pos:
                    if self.blind_mode:
                        display_char = '?'
                    else:
                        display_char = char if char != '\n' else ' '
                    color = curses.color_pair(COLOR_CURSOR) | curses.A_REVERSE
                else:
                    if self.blind_mode:
                        display_char = '·'
                    else:
                        display_char = char if char != '\n' else ' '
                    color = curses.color_pair(COLOR_PENDING)
                
                try:
                    self.stdscr.addstr(start_y + line_num, x, display_char, color)
                except curses.error:
                    pass
                
                x += 1
            
            pos = line_end
            line_num += 1

    def show_result(self):
        max_y, max_x = self.stdscr.getmaxyx()
        self.stdscr.clear()
        
        title = "=== 训练结果 ==="
        self.stdscr.addstr(2, (max_x - len(title)) // 2, title, curses.color_pair(COLOR_HIGHLIGHT) | curses.A_BOLD)
        
        lines = []
        lines.append(f"WPM (每分钟单词数): {self.stats.wpm:.2f}")
        lines.append(f"准确率: {self.stats.accuracy:.2f}%")
        lines.append(f"总字符数: {self.stats.total_chars}")
        lines.append(f"正确字符: {self.stats.correct_chars}")
        lines.append(f"错误字符: {self.stats.wrong_chars}")
        lines.append(f"用时: {self.stats.elapsed_time:.2f} 秒")
        
        top_errors = self.stats.top_errors(5)
        if top_errors:
            lines.append("")
            lines.append("最常错字符:")
            for char, count in top_errors:
                display_char = repr(char).strip("'")
                lines.append(f"  '{display_char}': {count} 次")
        
        slowest = self.stats.slowest_chars(5)
        if slowest:
            lines.append("")
            lines.append("输入最慢字符 (平均秒):")
            for char, avg_time in slowest:
                display_char = repr(char).strip("'")
                lines.append(f"  '{display_char}': {avg_time:.3f}s")
        
        pause_hotspots = self.stats.pause_hotspots[:3]
        if pause_hotspots:
            lines.append("")
            lines.append("停顿热点位置:")
            for pos, duration in pause_hotspots:
                lines.append(f"  第 {pos} 字符: {duration:.2f}s")
        
        start_y = 5
        for i, line in enumerate(lines):
            if start_y + i >= max_y - 2:
                break
            x = max(2, (max_x - len(line)) // 2)
            self.stdscr.addstr(start_y + i, x, line)
        
        prompt = "按任意键返回..."
        self.stdscr.addstr(max_y - 2, (max_x - len(prompt)) // 2, prompt, curses.color_pair(COLOR_PENDING) | curses.A_DIM)
        
        self.stdscr.refresh()
        self.stdscr.nodelay(False)
        try:
            self.stdscr.getch()
        except KeyboardInterrupt:
            pass
