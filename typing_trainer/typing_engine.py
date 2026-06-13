import curses
import time
from typing import Optional, Callable, List, Dict
from .stats import TypingStats
from .config import (
    COLOR_CORRECT, COLOR_WRONG, COLOR_CURSOR, COLOR_PENDING,
    COLOR_HIGHLIGHT, COLOR_RED, COLOR_BLUE, COLOR_MAGENTA
)
from .rhythm_visualizer import RhythmVisualizer


class TypingEngine:
    def __init__(self, stdscr, text: str, blind_mode: bool = False,
                 time_limit: Optional[int] = None,
                 progress_callback: Optional[Callable[[int, float], None]] = None,
                 opponent_data: Optional[List[Dict]] = None):
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
        self.progress_callback = progress_callback
        self.opponent_data = opponent_data or []
        self._init_colors()

    def _init_colors(self):
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(COLOR_CORRECT, curses.COLOR_GREEN, -1)
        curses.init_pair(COLOR_WRONG, curses.COLOR_WHITE, curses.COLOR_RED)
        curses.init_pair(COLOR_CURSOR, curses.COLOR_BLACK, curses.COLOR_CYAN)
        curses.init_pair(COLOR_PENDING, curses.COLOR_WHITE, -1)
        curses.init_pair(COLOR_HIGHLIGHT, curses.COLOR_YELLOW, -1)
        curses.init_pair(COLOR_RED, curses.COLOR_RED, -1)
        curses.init_pair(COLOR_BLUE, curses.COLOR_BLUE, -1)
        curses.init_pair(COLOR_MAGENTA, curses.COLOR_MAGENTA, -1)

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
            
            is_printable = (32 <= key <= 126) or key in (10, 13)
            if not is_printable:
                if key in (curses.KEY_BACKSPACE, 8, 127):
                    self._handle_backspace()
                continue
            
            if key in (10, 13):
                char = '\n'
            else:
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

            if self.progress_callback and self.started:
                try:
                    self.progress_callback(self.current_pos, self.stats.wpm)
                except Exception:
                    pass

            if self.current_pos >= len(self.text):
                self.finished = True
                self.stats.end_time = time.time()
                self.stats.calculate_rhythm_score()
                self.stats.calculate_section_stdevs()
        else:
            self.stats.record_wrong(char, expected_char, time_since_last)

    def _handle_backspace(self):
        pass

    def _render(self, max_y: int, max_x: int):
        self.stdscr.clear()

        info_y = 1
        self._render_status(info_y, max_x)

        text_y = info_y + 3

        opponent_lines = 0
        if self.opponent_data:
            opponent_lines = self._count_opponent_lines()

        text_area_height = max_y - text_y - 2 - opponent_lines - 1
        if text_area_height < 5:
            text_area_height = max_y - text_y - 2

        self._render_text(text_y, max_x, text_area_height)

        if self.opponent_data:
            opponent_y = text_y + text_area_height + 1
            self._render_opponents(opponent_y, max_x)

        hint_y = max_y - 1
        hint = "按 ESC 退出"
        self.stdscr.addstr(hint_y, 0, hint, curses.color_pair(COLOR_PENDING) | curses.A_DIM)

        self.stdscr.refresh()

    def _count_opponent_lines(self) -> int:
        count = 1
        for opp in self.opponent_data:
            if opp.get('id') != 'self':
                count += 1
        return count

    def _render_opponents(self, start_y: int, max_x: int):
        separator = "─" * (max_x - 2)
        try:
            self.stdscr.addstr(start_y, 0, "┌" + separator + "┐",
                              curses.color_pair(COLOR_HIGHLIGHT) | curses.A_DIM)
        except curses.error:
            pass

        y = start_y + 1
        header = "│ 对手进度" + " " * (max_x - 15) + "│"
        try:
            self.stdscr.addstr(y, 0, header[:max_x],
                              curses.color_pair(COLOR_HIGHLIGHT) | curses.A_BOLD)
        except curses.error:
            pass
        y += 1

        player_colors = [COLOR_BLUE, COLOR_MAGENTA, COLOR_CORRECT]
        color_idx = 0

        for opp in self.opponent_data:
            if opp.get('id') == 'self':
                continue

            name = opp.get('name', 'Unknown')[:12]
            pos = opp.get('pos', 0)
            wpm = opp.get('wpm', 0)
            finished = opp.get('finished', False)
            forfeit = opp.get('forfeit', False)
            total = max(1, len(self.text))
            percent = min(100.0, (pos / total) * 100)

            bar_width = max_x - 30
            filled = int((percent / 100) * bar_width)
            bar = '█' * filled + '░' * (bar_width - filled)

            color = player_colors[color_idx % len(player_colors)]
            color_idx += 1

            status = ""
            if forfeit:
                status = "【弃权】"
                color = COLOR_RED
            elif finished:
                finish_time = opp.get('finish_time', 0)
                status = f"【完成 {finish_time:.1f}s】"

            line = f"│ {name:<12} [{bar}] {wpm:5.1f} WPM {status}"
            line = line[:max_x - 1] + "│"

            try:
                self.stdscr.addstr(y, 0, line[:max_x], curses.color_pair(color))
            except curses.error:
                pass
            y += 1

        try:
            self.stdscr.addstr(y, 0, "└" + separator + "┘",
                              curses.color_pair(COLOR_HIGHLIGHT) | curses.A_DIM)
        except curses.error:
            pass

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
        x = 0
        
        while pos < len(text) and line_num < max_lines:
            char = text[pos]
            
            if char == '\n':
                if pos < self.current_pos:
                    color = curses.color_pair(COLOR_CORRECT)
                elif pos == self.current_pos:
                    color = curses.color_pair(COLOR_CURSOR) | curses.A_REVERSE
                else:
                    color = curses.color_pair(COLOR_PENDING)
                
                display_char = '$'
                if self.blind_mode:
                    if pos < self.current_pos:
                        display_char = ' '
                    elif pos == self.current_pos:
                        display_char = '?'
                    else:
                        display_char = '·'
                
                try:
                    self.stdscr.addstr(start_y + line_num, x, display_char, color)
                except curses.error:
                    pass
                
                line_num += 1
                x = 0
                pos += 1
                continue
            
            if pos < self.current_pos:
                if self.blind_mode:
                    display_char = ' '
                else:
                    display_char = char
                color = curses.color_pair(COLOR_CORRECT)
            elif pos == self.current_pos:
                if self.blind_mode:
                    display_char = '?'
                else:
                    display_char = char
                color = curses.color_pair(COLOR_CURSOR) | curses.A_REVERSE
            else:
                if self.blind_mode:
                    display_char = '·'
                else:
                    display_char = char
                color = curses.color_pair(COLOR_PENDING)
            
            try:
                self.stdscr.addstr(start_y + line_num, x, display_char, color)
            except curses.error:
                pass
            
            x += 1
            pos += 1
            
            if x >= max_x:
                line_num += 1
                x = 0

    def show_result(self, rhythm_report: Optional[List[str]] = None,
                    drill_comparison: Optional[List[str]] = None,
                    multiplayer_result: Optional[Dict] = None):
        max_y, max_x = self.stdscr.getmaxyx()
        self.stdscr.clear()
        self.stdscr.refresh()

        all_lines = []

        title = "=== 训练结果 ==="
        all_lines.append(title)
        all_lines.append("")

        if multiplayer_result:
            winner_id = multiplayer_result.get('winner_id')
            players = multiplayer_result.get('players', [])

            if winner_id == self.stats.__dict__.get('player_id', ''):
                all_lines.append("🎉 恭喜！您获胜了！")
            elif winner_id:
                winner_name = next((p.get('name', 'Unknown') for p in players
                                   if p.get('id') == winner_id), 'Unknown')
                all_lines.append(f"获胜者: {winner_name}")
            all_lines.append("")

            for p in players:
                pid = p.get('id', '')
                name = p.get('name', 'Unknown')
                finish_time = p.get('finish_time')
                forfeit = p.get('forfeit', False)
                stats = p.get('final_stats', {})

                is_self = pid == self.stats.__dict__.get('player_id', '')
                prefix = "★ " if is_self else "  "

                if forfeit:
                    all_lines.append(f"{prefix}{name}: 弃权")
                elif finish_time is not None:
                    wpm = stats.get('wpm', 0)
                    acc = stats.get('accuracy', 0)
                    all_lines.append(
                        f"{prefix}{name}: {finish_time:.1f}s | WPM: {wpm:.1f} | 准确率: {acc:.1f}%"
                    )
                else:
                    all_lines.append(f"{prefix}{name}: 进行中")

            all_lines.append("")
            all_lines.append("-" * 40)
            all_lines.append("")

        all_lines.append(f"WPM (每分钟单词数): {self.stats.wpm:.2f}")
        all_lines.append(f"准确率: {self.stats.accuracy:.2f}%")
        all_lines.append(f"总字符数: {self.stats.total_chars}")
        all_lines.append(f"正确字符: {self.stats.correct_chars}")
        all_lines.append(f"错误字符: {self.stats.wrong_chars}")
        all_lines.append(f"用时: {self.stats.elapsed_time:.2f} 秒")
        all_lines.append(f"节奏评分: {self.stats.rhythm_score:.1f} / 100")

        top_errors = self.stats.top_errors(5)
        if top_errors:
            all_lines.append("")
            all_lines.append("最常错字符:")
            for char, count in top_errors:
                display_char = repr(char).strip("'")
                all_lines.append(f"  '{display_char}': {count} 次")

        slowest = self.stats.slowest_chars(5)
        if slowest:
            all_lines.append("")
            all_lines.append("输入最慢字符 (平均秒):")
            for char, avg_time in slowest:
                display_char = repr(char).strip("'")
                all_lines.append(f"  '{display_char}': {avg_time:.3f}s")

        if drill_comparison:
            all_lines.append("")
            all_lines.extend(drill_comparison)

        if rhythm_report:
            all_lines.extend(rhythm_report)

        total_lines = len(all_lines)
        start_line = 0

        self.stdscr.nodelay(False)
        curses.curs_set(0)

        while True:
            self.stdscr.clear()

            display_y = 1
            for i in range(start_line, min(start_line + max_y - 3, total_lines)):
                line = all_lines[i]
                line_display = line[:max_x - 2]

                if i == 0:
                    attr = curses.color_pair(COLOR_HIGHLIGHT) | curses.A_BOLD
                    x = (max_x - len(line_display)) // 2
                elif "恭喜" in line or "获胜者" in line:
                    attr = curses.color_pair(COLOR_HIGHLIGHT) | curses.A_BOLD
                    x = 2
                elif line.startswith("=") or line.startswith("🎵") or line.startswith("📊"):
                    attr = curses.color_pair(COLOR_HIGHLIGHT) | curses.A_BOLD
                    x = 2
                elif line.startswith("★"):
                    attr = curses.color_pair(COLOR_HIGHLIGHT)
                    x = 2
                elif "ms │" in line:
                    parts = line.split("│", 1)
                    if len(parts) == 2:
                        self.stdscr.addstr(display_y, 2, parts[0] + "│",
                                          curses.color_pair(COLOR_PENDING) | curses.A_DIM)
                        plot_part = parts[1]
                        x_pos = 2 + len(parts[0]) + 1
                        for ci, ch in enumerate(plot_part):
                            if ch == '●':
                                self.stdscr.addstr(display_y, x_pos + ci, ch,
                                                  curses.color_pair(COLOR_RED))
                            elif ch in ('·', '█', '░', '─', '●', '└'):
                                self.stdscr.addstr(display_y, x_pos + ci, ch,
                                                  curses.color_pair(COLOR_MENU))
                            else:
                                self.stdscr.addstr(display_y, x_pos + ci, ch)
                        display_y += 1
                        continue
                    attr = curses.color_pair(COLOR_PENDING)
                    x = 2
                else:
                    attr = curses.color_pair(COLOR_PENDING)
                    x = 2

                try:
                    self.stdscr.addstr(display_y, x, line_display, attr)
                except curses.error:
                    pass
                display_y += 1

            if total_lines > max_y - 3:
                scroll_info = f"↑↓ 滚动 ({start_line + 1}/{min(start_line + max_y - 3, total_lines)}/{total_lines})"
                try:
                    self.stdscr.addstr(max_y - 2, 2, scroll_info,
                                      curses.color_pair(COLOR_HIGHLIGHT) | curses.A_DIM)
                except curses.error:
                    pass

            prompt = "按任意键退出 | 滚动: ↑↓"
            try:
                self.stdscr.addstr(max_y - 1, (max_x - len(prompt)) // 2, prompt,
                                  curses.color_pair(COLOR_PENDING) | curses.A_DIM)
            except curses.error:
                pass

            self.stdscr.refresh()

            try:
                key = self.stdscr.getch()
            except KeyboardInterrupt:
                break

            if key == curses.KEY_UP:
                start_line = max(0, start_line - 1)
            elif key == curses.KEY_DOWN:
                start_line = max(0, min(total_lines - (max_y - 3), start_line + 1))
            elif key == curses.KEY_PPAGE:
                start_line = max(0, start_line - (max_y - 3))
            elif key == curses.KEY_NPAGE:
                start_line = max(0, min(total_lines - (max_y - 3), start_line + (max_y - 3)))
            else:
                break
