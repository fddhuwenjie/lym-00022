import curses
import random
import time
from typing import Optional, List, Dict
from .courses import list_courses, get_course, Lesson
from .typing_engine import TypingEngine
from .storage import Storage, Record, CustomText
from .visualizer import ASCIIChart, ChartData
from .rhythm_visualizer import RhythmVisualizer
from .drill_analyzer import DrillAnalyzer
from .multiplayer import MultiplayerServer, MultiplayerClient
from .config import (
    COLOR_CORRECT, COLOR_WRONG, COLOR_CURSOR, COLOR_PENDING,
    COLOR_HIGHLIGHT, COLOR_MENU, COLOR_RED, COLOR_BLUE, COLOR_MAGENTA,
    DIFFICULTY_LEVELS, DEFAULT_MULTIPLAYER_PORT
)


class TypingTrainerCLI:
    def __init__(self, stdscr, mode: str = "normal",
                 host_port: int = DEFAULT_MULTIPLAYER_PORT,
                 join_addr: Optional[str] = None):
        self.stdscr = stdscr
        self.blind_mode = False
        self.time_limit: Optional[int] = None
        self.current_menu = "main"
        self.selected_idx = 0
        self.mode = mode
        self.host_port = host_port
        self.join_addr = join_addr
        self.server: Optional[MultiplayerServer] = None
        self.client: Optional[MultiplayerClient] = None
        self.multiplayer_players: List[Dict] = []
        self.multiplayer_started = False
        self.multiplayer_game_text = ""
        self.multiplayer_result: Optional[Dict] = None
        self.countdown = 0
        self._init_colors()

    def _init_colors(self):
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(COLOR_CORRECT, curses.COLOR_GREEN, -1)
        curses.init_pair(COLOR_WRONG, curses.COLOR_WHITE, curses.COLOR_RED)
        curses.init_pair(COLOR_CURSOR, curses.COLOR_BLACK, curses.COLOR_CYAN)
        curses.init_pair(COLOR_PENDING, curses.COLOR_WHITE, -1)
        curses.init_pair(COLOR_HIGHLIGHT, curses.COLOR_YELLOW, -1)
        curses.init_pair(COLOR_MENU, curses.COLOR_CYAN, -1)
        curses.init_pair(COLOR_RED, curses.COLOR_RED, -1)
        curses.init_pair(COLOR_BLUE, curses.COLOR_BLUE, -1)
        curses.init_pair(COLOR_MAGENTA, curses.COLOR_MAGENTA, -1)

    def run(self):
        curses.curs_set(0)
        self.stdscr.keypad(True)

        if self.mode == "host":
            self._run_host_mode()
        elif self.mode == "join":
            self._run_join_mode()
        elif self.mode == "drill":
            self._run_drill_mode()
        elif self.mode == "rhythm_history":
            self._run_rhythm_history()
        else:
            self._main_loop()

    def _main_loop(self):
        while True:
            max_y, max_x = self.stdscr.getmaxyx()
            
            if self.current_menu == "main":
                self._draw_main_menu(max_y, max_x)
            elif self.current_menu == "courses":
                self._draw_courses_menu(max_y, max_x)
            elif self.current_menu == "custom":
                self._draw_custom_menu(max_y, max_x)
            elif self.current_menu == "settings":
                self._draw_settings_menu(max_y, max_x)
            elif self.current_menu == "history":
                self._draw_history_menu(max_y, max_x)
            elif self.current_menu == "progress":
                self._draw_progress_menu(max_y, max_x)
            
            try:
                key = self.stdscr.getch()
            except KeyboardInterrupt:
                break
            
            if self.current_menu == "main":
                if not self._handle_main_menu_input(key):
                    break
            elif self.current_menu == "courses":
                self._handle_courses_input(key)
            elif self.current_menu == "custom":
                self._handle_custom_input(key)
            elif self.current_menu == "settings":
                self._handle_settings_input(key)
            elif self.current_menu == "history":
                self._handle_history_input(key)
            elif self.current_menu == "progress":
                self._handle_progress_input(key)

    def _draw_main_menu(self, max_y: int, max_x: int):
        self.stdscr.clear()
        
        title = "⌨  终端打字训练"
        subtitle = "Terminal Typing Trainer v1.0"
        
        self.stdscr.addstr(2, (max_x - len(title)) // 2, title, 
                          curses.color_pair(COLOR_HIGHLIGHT) | curses.A_BOLD)
        self.stdscr.addstr(4, (max_x - len(subtitle)) // 2, subtitle, 
                          curses.color_pair(COLOR_PENDING) | curses.A_DIM)
        
        menu_items = [
            "1. 开始训练 - 选择课程",
            "2. 自定义文本",
            "3. 专项薄弱训练 (--drill)",
            "4. 多人竞速对战",
            "5. 历史记录",
            "6. 进步曲线",
            "7. 节奏评分历史",
            "8. 设置选项",
            "0. 退出"
        ]
        
        settings_info = []
        if self.blind_mode:
            settings_info.append("盲打模式: 开")
        if self.time_limit:
            minutes = self.time_limit // 60
            seconds = self.time_limit % 60
            settings_info.append(f"限时: {minutes}分{seconds}秒")
        if settings_info:
            info_text = "  [" + " | ".join(settings_info) + "]"
            self.stdscr.addstr(6, (max_x - len(info_text)) // 2, info_text,
                              curses.color_pair(COLOR_HIGHLIGHT))
        
        start_y = 9
        for i, item in enumerate(menu_items):
            y = start_y + i * 2
            x = (max_x - len(item)) // 2
            
            if i == self.selected_idx:
                self.stdscr.addstr(y, x, f"> {item}", 
                                  curses.color_pair(COLOR_CURSOR) | curses.A_BOLD)
            else:
                self.stdscr.addstr(y, x, f"  {item}", 
                                  curses.color_pair(COLOR_MENU))
        
        hint = "使用 ↑↓ 键选择，回车确认，ESC 返回，Q 退出"
        self.stdscr.addstr(max_y - 2, (max_x - len(hint)) // 2, hint,
                          curses.color_pair(COLOR_PENDING) | curses.A_DIM)
        
        self.stdscr.refresh()

    def _handle_main_menu_input(self, key: int) -> bool:
        if key == ord('q') or key == ord('Q'):
            return False

        menu_items = 9

        if key == curses.KEY_UP:
            self.selected_idx = (self.selected_idx - 1) % menu_items
        elif key == curses.KEY_DOWN:
            self.selected_idx = (self.selected_idx + 1) % menu_items
        elif key == curses.KEY_ENTER or key == 10 or key == 13:
            if self.selected_idx == 0:
                self.current_menu = "courses"
                self.selected_idx = 0
            elif self.selected_idx == 1:
                self.current_menu = "custom"
                self.selected_idx = 0
            elif self.selected_idx == 2:
                self._run_drill_mode()
            elif self.selected_idx == 3:
                self._run_multiplayer_menu()
            elif self.selected_idx == 4:
                self.current_menu = "history"
                self.selected_idx = 0
            elif self.selected_idx == 5:
                self.current_menu = "progress"
                self.selected_idx = 0
            elif self.selected_idx == 6:
                self._run_rhythm_history()
            elif self.selected_idx == 7:
                self.current_menu = "settings"
                self.selected_idx = 0
            elif self.selected_idx == 8:
                return False
        elif key == 27:
            return False

        return True

    def _draw_courses_menu(self, max_y: int, max_x: int):
        self.stdscr.clear()
        
        title = "=== 选择课程 ==="
        self.stdscr.addstr(1, (max_x - len(title)) // 2, title, 
                          curses.color_pair(COLOR_HIGHLIGHT) | curses.A_BOLD)
        
        courses = list_courses()
        start_y = 4
        
        for i, course in enumerate(courses):
            y = start_y + i * 3
            
            diff_label = DIFFICULTY_LEVELS.get(course.difficulty, "未知")
            diff_stars = "★" * course.difficulty + "☆" * (6 - course.difficulty)
            
            course_line = f"  [{course.id}] {course.name}"
            info_line = f"      难度: {diff_stars} ({diff_label})  -  {course.description}"
            
            if i == self.selected_idx:
                self.stdscr.addstr(y, 2, f"> {course.name}", 
                                  curses.color_pair(COLOR_CURSOR) | curses.A_BOLD)
                self.stdscr.addstr(y + 1, 4, info_line, 
                                  curses.color_pair(COLOR_PENDING) | curses.A_DIM)
            else:
                self.stdscr.addstr(y, 2, course_line, curses.color_pair(COLOR_MENU))
                self.stdscr.addstr(y + 1, 4, info_line, 
                                  curses.color_pair(COLOR_PENDING) | curses.A_DIM)
        
        best_record = Storage.get_best_wpm()
        if best_record:
            best_line = f"个人最佳 WPM: {best_record.wpm:.2f}"
            self.stdscr.addstr(max_y - 4, 2, best_line, 
                              curses.color_pair(COLOR_HIGHLIGHT))
        
        hint = "↑↓ 选择  回车开始  ESC 返回"
        self.stdscr.addstr(max_y - 2, (max_x - len(hint)) // 2, hint,
                          curses.color_pair(COLOR_PENDING) | curses.A_DIM)
        
        self.stdscr.refresh()

    def _handle_courses_input(self, key: int):
        courses = list_courses()
        
        if key == 27:
            self.current_menu = "main"
            self.selected_idx = 0
            return
        
        if key == curses.KEY_UP:
            self.selected_idx = max(0, self.selected_idx - 1)
        elif key == curses.KEY_DOWN:
            self.selected_idx = min(len(courses) - 1, self.selected_idx + 1)
        elif key == curses.KEY_ENTER or key == 10 or key == 13:
            if 0 <= self.selected_idx < len(courses):
                self._start_course(courses[self.selected_idx])

    def _start_course(self, course: Lesson):
        text = random.choice(course.texts)
        engine = TypingEngine(self.stdscr, text, self.blind_mode, self.time_limit)
        stats = engine.run()

        if not engine.quit_early and stats.total_chars > 0:
            rhythm_report = RhythmVisualizer.generate_rhythm_report(stats, width=60)
            record = Storage.create_record_from_stats(
                stats,
                course_id=course.id,
                course_name=course.name,
                blind_mode=self.blind_mode,
                time_limit=self.time_limit,
                is_custom=False
            )
            Storage.add_record(record)
            engine.show_result(rhythm_report=rhythm_report)

    def _draw_custom_menu(self, max_y: int, max_x: int):
        self.stdscr.clear()
        
        title = "=== 自定义文本 ==="
        self.stdscr.addstr(1, (max_x - len(title)) // 2, title,
                          curses.color_pair(COLOR_HIGHLIGHT) | curses.A_BOLD)
        
        custom_texts = Storage.get_all_custom_texts()
        
        menu_items = [
            "新建自定义文本",
            "输入临时文本练习"
        ]
        
        for i, item in enumerate(menu_items):
            y = 4 + i * 2
            if i == self.selected_idx and self.selected_idx < 2:
                self.stdscr.addstr(y, 2, f"> {item}",
                                  curses.color_pair(COLOR_CURSOR) | curses.A_BOLD)
            else:
                self.stdscr.addstr(y, 2, f"  {item}",
                                  curses.color_pair(COLOR_MENU))
        
        if custom_texts:
            self.stdscr.addstr(9, 2, "已保存的文本:", 
                              curses.color_pair(COLOR_HIGHLIGHT) | curses.A_UNDERLINE)
            y = 11
            for i, ct in enumerate(custom_texts):
                list_idx = i + 2
                line = f"  [{ct.id}] {ct.name} ({len(ct.content)} 字符)"
                if self.selected_idx == list_idx:
                    self.stdscr.addstr(y, 2, f"> {line[2:]}",
                                      curses.color_pair(COLOR_CURSOR) | curses.A_BOLD)
                else:
                    self.stdscr.addstr(y, 2, line,
                                      curses.color_pair(COLOR_PENDING))
                y += 1
        
        hint = "↑↓ 选择  回车确认  D 删除  ESC 返回"
        self.stdscr.addstr(max_y - 2, (max_x - len(hint)) // 2, hint,
                          curses.color_pair(COLOR_PENDING) | curses.A_DIM)
        
        self.stdscr.refresh()

    def _handle_custom_input(self, key: int):
        custom_texts = Storage.get_all_custom_texts()
        total_items = 2 + len(custom_texts)
        
        if key == 27:
            self.current_menu = "main"
            self.selected_idx = 0
            return
        
        if key == curses.KEY_UP:
            self.selected_idx = max(0, self.selected_idx - 1)
        elif key == curses.KEY_DOWN:
            self.selected_idx = min(total_items - 1, self.selected_idx + 1)
        elif key == curses.KEY_ENTER or key == 10 or key == 13:
            if self.selected_idx == 0:
                self._create_custom_text()
            elif self.selected_idx == 1:
                self._temp_text_practice()
            elif self.selected_idx >= 2:
                ct_idx = self.selected_idx - 2
                if ct_idx < len(custom_texts):
                    ct = custom_texts[ct_idx]
                    self._start_custom_practice(ct)
        elif key in (ord('d'), ord('D')):
            if self.selected_idx >= 2:
                ct_idx = self.selected_idx - 2
                if ct_idx < len(custom_texts):
                    ct = custom_texts[ct_idx]
                    Storage.delete_custom_text(ct.id)
                    self.selected_idx = max(0, self.selected_idx - 1)

    def _create_custom_text(self):
        curses.echo()
        curses.curs_set(1)
        self.stdscr.clear()
        
        self.stdscr.addstr(2, 2, "输入文本名称 (回车确认):", curses.color_pair(COLOR_HIGHLIGHT))
        self.stdscr.clrtoeol()
        self.stdscr.refresh()
        
        name = ""
        while True:
            key = self.stdscr.getch()
            if key in (curses.KEY_ENTER, 10, 13):
                break
            elif key in (27,):
                curses.noecho()
                curses.curs_set(0)
                return
            elif key in (curses.KEY_BACKSPACE, 8, 127):
                if name:
                    name = name[:-1]
                    y, x = self.stdscr.getyx()
                    self.stdscr.addstr(y, x - 1, " ")
                    self.stdscr.move(y, x - 1)
            elif 32 <= key <= 126:
                name += chr(key)
        
        self.stdscr.addstr(4, 2, "输入文本内容 (按 Ctrl+G 结束):", curses.color_pair(COLOR_HIGHLIGHT))
        self.stdscr.move(5, 2)
        self.stdscr.clrtobot()
        self.stdscr.refresh()
        
        content = ""
        max_y, max_x = self.stdscr.getmaxyx()
        while True:
            try:
                key = self.stdscr.getch()
            except KeyboardInterrupt:
                break
            
            if key == 7:
                break
            elif key == 27:
                curses.noecho()
                curses.curs_set(0)
                return
            elif key in (curses.KEY_BACKSPACE, 8, 127):
                if content:
                    content = content[:-1]
                    y, x = self.stdscr.getyx()
                    if x > 2:
                        self.stdscr.addstr(y, x - 1, " ")
                        self.stdscr.move(y, x - 1)
                    elif y > 5:
                        self.stdscr.move(y - 1, max_x - 1)
                        self.stdscr.addstr(y - 1, max_x - 1, " ")
            elif key in (10, 13):
                content += '\n'
                self.stdscr.addstr("\n")
            elif 32 <= key <= 126 or key > 127:
                if key <= 126:
                    content += chr(key)
        
        curses.noecho()
        curses.curs_set(0)
        
        if name and content:
            Storage.add_custom_text(name, content)

    def _temp_text_practice(self):
        curses.echo()
        curses.curs_set(1)
        self.stdscr.clear()
        
        self.stdscr.addstr(2, 2, "输入练习文本 (按 Ctrl+G 开始):", curses.color_pair(COLOR_HIGHLIGHT))
        self.stdscr.move(4, 2)
        self.stdscr.refresh()
        
        content = ""
        max_y, max_x = self.stdscr.getmaxyx()
        
        while True:
            try:
                key = self.stdscr.getch()
            except KeyboardInterrupt:
                curses.noecho()
                curses.curs_set(0)
                return
            
            if key == 7:
                break
            elif key == 27:
                curses.noecho()
                curses.curs_set(0)
                return
            elif key in (curses.KEY_BACKSPACE, 8, 127):
                if content:
                    content = content[:-1]
                    y, x = self.stdscr.getyx()
                    if x > 2:
                        self.stdscr.addstr(y, x - 1, " ")
                        self.stdscr.move(y, x - 1)
            elif key in (10, 13):
                content += '\n'
                self.stdscr.addstr("\n")
            elif 32 <= key <= 126:
                content += chr(key)
        
        curses.noecho()
        curses.curs_set(0)
        
        if content:
            engine = TypingEngine(self.stdscr, content, self.blind_mode, self.time_limit)
            stats = engine.run()

            if not engine.quit_early and stats.total_chars > 0:
                rhythm_report = RhythmVisualizer.generate_rhythm_report(stats, width=60)
                record = Storage.create_record_from_stats(
                    stats,
                    course_id=None,
                    course_name="临时练习",
                    blind_mode=self.blind_mode,
                    time_limit=self.time_limit,
                    is_custom=True
                )
                Storage.add_record(record)
                engine.show_result(rhythm_report=rhythm_report)

    def _start_custom_practice(self, ct: CustomText):
        engine = TypingEngine(self.stdscr, ct.content, self.blind_mode, self.time_limit)
        stats = engine.run()

        if not engine.quit_early and stats.total_chars > 0:
            rhythm_report = RhythmVisualizer.generate_rhythm_report(stats, width=60)
            record = Storage.create_record_from_stats(
                stats,
                course_id=None,
                course_name=ct.name,
                blind_mode=self.blind_mode,
                time_limit=self.time_limit,
                is_custom=True
            )
            Storage.add_record(record)
            engine.show_result(rhythm_report=rhythm_report)

    def _draw_settings_menu(self, max_y: int, max_x: int):
        self.stdscr.clear()
        
        title = "=== 设置 ==="
        self.stdscr.addstr(1, (max_x - len(title)) // 2, title,
                          curses.color_pair(COLOR_HIGHLIGHT) | curses.A_BOLD)
        
        blind_status = "开启" if self.blind_mode else "关闭"
        if self.time_limit:
            minutes = self.time_limit // 60
            seconds = self.time_limit % 60
            if minutes > 0:
                time_status = f"{minutes}分{seconds}秒" if seconds > 0 else f"{minutes}分钟"
            else:
                time_status = f"{seconds}秒"
        else:
            time_status = "关闭"
        
        menu_items = [
            (0, f"盲打模式: {blind_status}", "切换盲打模式开关"),
            (1, "--- 限时设置 ---", ""),
            (2, "限时: 30 秒", "设置 30 秒限时挑战"),
            (3, "限时: 1 分钟", "设置 1 分钟限时挑战"),
            (4, "限时: 2 分钟", "设置 2 分钟限时挑战"),
            (5, "限时: 5 分钟", "设置 5 分钟限时挑战"),
            (6, "关闭限时", "关闭限时挑战模式"),
        ]
        
        start_y = 4
        for i, (idx, label, desc) in enumerate(menu_items):
            y = start_y + i
            
            if idx == 1:
                self.stdscr.addstr(y, 2, f"  {label}",
                                  curses.color_pair(COLOR_PENDING) | curses.A_DIM)
            else:
                selectable_idx = self._settings_index_to_selectable(idx)
                is_selected = (selectable_idx == self.selected_idx)
                
                if is_selected:
                    self.stdscr.addstr(y, 2, f"> {label}",
                                      curses.color_pair(COLOR_CURSOR) | curses.A_BOLD)
                else:
                    self.stdscr.addstr(y, 2, f"  {label}",
                                      curses.color_pair(COLOR_MENU))
        
        status_y = start_y + len(menu_items) + 2
        current_status = f"当前 - 盲打: {blind_status}  |  限时: {time_status}"
        self.stdscr.addstr(status_y, 2, current_status,
                          curses.color_pair(COLOR_HIGHLIGHT))
        
        desc_y = status_y + 2
        self.stdscr.addstr(desc_y, 2, "说明:", curses.color_pair(COLOR_HIGHLIGHT))
        self.stdscr.addstr(desc_y + 1, 4, "盲打模式: 隐藏待输入字符，只显示光标位置，强制练习盲打",
                          curses.color_pair(COLOR_PENDING) | curses.A_DIM)
        self.stdscr.addstr(desc_y + 2, 4, "限时挑战: 在规定时间内尽可能多地输入字符",
                          curses.color_pair(COLOR_PENDING) | curses.A_DIM)
        
        hint = "↑↓ 选择  回车确认  ESC 返回"
        self.stdscr.addstr(max_y - 2, (max_x - len(hint)) // 2, hint,
                          curses.color_pair(COLOR_PENDING) | curses.A_DIM)
        
        self.stdscr.refresh()

    def _settings_index_to_selectable(self, idx: int) -> int:
        if idx == 0:
            return 0
        elif idx >= 2:
            return idx - 1
        return -1

    def _selectable_to_settings_index(self, selectable_idx: int) -> int:
        if selectable_idx == 0:
            return 0
        else:
            return selectable_idx + 1

    def _handle_settings_input(self, key: int):
        if key == 27:
            self.current_menu = "main"
            self.selected_idx = 0
            return
        
        num_selectable = 6
        
        if key == curses.KEY_UP:
            self.selected_idx = max(0, self.selected_idx - 1)
        elif key == curses.KEY_DOWN:
            self.selected_idx = min(num_selectable - 1, self.selected_idx + 1)
        elif key == curses.KEY_ENTER or key == 10 or key == 13:
            settings_idx = self._selectable_to_settings_index(self.selected_idx)
            if settings_idx == 0:
                self.blind_mode = not self.blind_mode
            elif settings_idx == 2:
                self.time_limit = 30
            elif settings_idx == 3:
                self.time_limit = 60
            elif settings_idx == 4:
                self.time_limit = 120
            elif settings_idx == 5:
                self.time_limit = 300
            elif settings_idx == 6:
                self.time_limit = None

    def _draw_history_menu(self, max_y: int, max_x: int):
        self.stdscr.clear()
        
        title = "=== 历史记录 ==="
        self.stdscr.addstr(1, (max_x - len(title)) // 2, title,
                          curses.color_pair(COLOR_HIGHLIGHT) | curses.A_BOLD)
        
        records = Storage.get_recent_records(20)
        
        if not records:
            self.stdscr.addstr(5, (max_x - 20) // 2, "暂无历史记录",
                              curses.color_pair(COLOR_PENDING) | curses.A_DIM)
        else:
            header = f"{'#':<4}{'课程':<20}{'WPM':<8}{'准确率':<10}{'用时':<10}{'日期':<20}"
            self.stdscr.addstr(3, 2, header[:max_x - 4], 
                              curses.color_pair(COLOR_HIGHLIGHT) | curses.A_UNDERLINE)
            
            start_y = 5
            display_count = min(len(records), max_y - start_y - 2)
            
            for i in range(display_count):
                idx = i + self.selected_idx
                if idx >= len(records):
                    break
                
                record = records[idx]
                y = start_y + i
                
                date_str = record.timestamp[:19].replace('T', ' ')
                line = f"{record.id:<4}{record.course_name[:18]:<20}{record.wpm:<8.1f}{record.accuracy:<9.1f}%{record.duration:<9.1f}s{date_str:<20}"
                
                mode_tags = []
                if record.blind_mode:
                    mode_tags.append("盲")
                if record.time_limit:
                    mode_tags.append("限")
                if mode_tags:
                    line += " [" + "".join(mode_tags) + "]"
                
                if i == 0 and len(records) > display_count:
                    pass
                
                if idx == self.selected_idx:
                    self.stdscr.addstr(y, 2, line[:max_x - 4],
                                      curses.color_pair(COLOR_CURSOR) | curses.A_BOLD)
                else:
                    self.stdscr.addstr(y, 2, line[:max_x - 4],
                                      curses.color_pair(COLOR_PENDING))
        
        total_line = f"共 {len(records)} 条记录"
        self.stdscr.addstr(max_y - 4, 2, total_line,
                          curses.color_pair(COLOR_PENDING) | curses.A_DIM)
        
        hint = "↑↓ 浏览  ESC 返回"
        self.stdscr.addstr(max_y - 2, (max_x - len(hint)) // 2, hint,
                          curses.color_pair(COLOR_PENDING) | curses.A_DIM)
        
        self.stdscr.refresh()

    def _handle_history_input(self, key: int):
        records = Storage.get_recent_records(20)
        
        if key == 27:
            self.current_menu = "main"
            self.selected_idx = 0
            return
        
        if key == curses.KEY_UP:
            self.selected_idx = max(0, self.selected_idx - 1)
        elif key == curses.KEY_DOWN:
            self.selected_idx = min(len(records) - 1, self.selected_idx + 1)

    def _draw_progress_menu(self, max_y: int, max_x: int):
        self.stdscr.clear()
        
        title = "=== 进步曲线 ==="
        self.stdscr.addstr(1, (max_x - len(title)) // 2, title,
                          curses.color_pair(COLOR_HIGHLIGHT) | curses.A_BOLD)
        
        records = Storage.get_all_records()
        records.sort(key=lambda r: r.timestamp)
        
        if len(records) < 2:
            self.stdscr.addstr(5, (max_x - 30) // 2, 
                              "需要至少 2 条记录才能生成进步曲线",
                              curses.color_pair(COLOR_PENDING) | curses.A_DIM)
        else:
            wpm_values = [r.wpm for r in records]
            acc_values = [r.accuracy for r in records]
            labels = [f"#{i+1}" for i in range(len(records))]
            
            chart_width = min(max_x - 10, 70)
            
            wpm_data = ChartData(label="WPM", values=wpm_values, labels=labels)
            wpm_chart = ASCIIChart.line_chart(
                wpm_data, width=chart_width, height=12, title="WPM 进步曲线"
            )
            
            y = 3
            for line in wpm_chart:
                if y >= max_y - 5:
                    break
                x = max(2, (max_x - len(line)) // 2)
                self.stdscr.addstr(y, x, line, curses.color_pair(COLOR_MENU))
                y += 1
            
            acc_y = y + 2
            if acc_y < max_y - 5:
                acc_data = ChartData(label="准确率(%)", values=acc_values, labels=labels)
                acc_chart = ASCIIChart.line_chart(
                    acc_data, width=chart_width, height=10, title="准确率进步曲线"
                )
                for line in acc_chart:
                    if acc_y >= max_y - 5:
                        break
                    x = max(2, (max_x - len(line)) // 2)
                    self.stdscr.addstr(acc_y, x, line, curses.color_pair(COLOR_CORRECT))
                    acc_y += 1
            
            summary_y = min(max_y - 5, acc_y + 2)
            if summary_y < max_y - 3:
                avg_wpm = sum(wpm_values) / len(wpm_values)
                avg_acc = sum(acc_values) / len(acc_values)
                best_wpm = max(wpm_values)
                improvement = wpm_values[-1] - wpm_values[0]
                
                summary = f"总练习: {len(records)} 次  |  平均 WPM: {avg_wpm:.1f}  |  平均准确率: {avg_acc:.1f}%  |  最佳 WPM: {best_wpm:.1f}  |  进步: {improvement:+.1f} WPM"
                x = max(2, (max_x - len(summary)) // 2)
                self.stdscr.addstr(summary_y, x, summary[:max_x - 4],
                                  curses.color_pair(COLOR_HIGHLIGHT))
        
        hint = "ESC 返回"
        self.stdscr.addstr(max_y - 2, (max_x - len(hint)) // 2, hint,
                          curses.color_pair(COLOR_PENDING) | curses.A_DIM)
        
        self.stdscr.refresh()

    def _handle_progress_input(self, key: int):
        if key == 27 or key == curses.KEY_ENTER or key == 10 or key == 13:
            self.current_menu = "main"
            self.selected_idx = 0

    def _run_drill_mode(self):
        analyzer = DrillAnalyzer()

        if not analyzer.has_enough_history():
            count = analyzer.get_history_count()
            self.stdscr.clear()
            max_y, max_x = self.stdscr.getmaxyx()

            title = "=== 专项薄弱训练 ==="
            self.stdscr.addstr(2, (max_x - len(title)) // 2, title,
                              curses.color_pair(COLOR_HIGHLIGHT) | curses.A_BOLD)

            lines = [
                f"您目前只有 {count} 次练习记录。",
                f"专项训练需要至少 5 次练习记录来分析您的薄弱点。",
                "",
                "请先完成几次常规练习，然后再使用专项训练模式。",
                "",
                "薄弱分析将根据您的历史错字分布和按键停顿，",
                "自动识别薄弱字符和双字母组合，生成针对性练习。"
            ]

            y = 5
            for line in lines:
                x = max(2, (max_x - len(line)) // 2)
                self.stdscr.addstr(y, x, line, curses.color_pair(COLOR_PENDING))
                y += 1

            prompt = "按任意键返回主菜单..."
            self.stdscr.addstr(max_y - 2, (max_x - len(prompt)) // 2, prompt,
                              curses.color_pair(COLOR_PENDING) | curses.A_DIM)
            self.stdscr.refresh()
            self.stdscr.getch()
            return

        if not analyzer.load_analysis():
            return

        drill_text = analyzer.generate_drill_text()
        if not drill_text:
            return

        self.stdscr.clear()
        max_y, max_x = self.stdscr.getmaxyx()

        title = "=== 专项薄弱训练 ==="
        self.stdscr.addstr(1, (max_x - len(title)) // 2, title,
                          curses.color_pair(COLOR_HIGHLIGHT) | curses.A_BOLD)

        summary = analyzer.get_weakness_summary()
        self.stdscr.addstr(3, 2, "分析结果:", curses.color_pair(COLOR_HIGHLIGHT))
        self.stdscr.addstr(4, 4, summary, curses.color_pair(COLOR_PENDING))

        self.stdscr.addstr(6, 2, "练习文本预览 (前 200 字符):",
                          curses.color_pair(COLOR_HIGHLIGHT))
        preview = drill_text[:200] + ("..." if len(drill_text) > 200 else "")
        y = 8
        x = 4
        for ch in preview:
            if x >= max_x - 2:
                y += 1
                x = 4
                if y >= max_y - 4:
                    break
            self.stdscr.addstr(y, x, ch, curses.color_pair(COLOR_PENDING))
            x += 1

        prompt = "按任意键开始练习，按 ESC 返回..."
        self.stdscr.addstr(max_y - 2, (max_x - len(prompt)) // 2, prompt,
                          curses.color_pair(COLOR_PENDING) | curses.A_DIM)
        self.stdscr.refresh()

        key = self.stdscr.getch()
        if key == 27:
            return

        def progress_cb(pos, wpm):
            pass

        engine = TypingEngine(
            self.stdscr, drill_text, self.blind_mode, self.time_limit,
            progress_callback=progress_cb
        )
        stats = engine.run()

        if not engine.quit_early and stats.total_chars > 0:
            stats.is_drill = True
            stats.drill_weak_chars = analyzer.weak_chars
            stats.drill_weak_bigrams = analyzer.weak_bigrams

            rhythm_report = RhythmVisualizer.generate_rhythm_report(stats, width=60)
            comparison = analyzer.compare_with_last_drill(
                stats.wpm, stats.accuracy, stats.rhythm_score
            )
            comparison_bars = analyzer.get_comparison_bars(comparison)

            record = Storage.create_record_from_stats(
                stats,
                course_id=None,
                course_name="专项训练",
                blind_mode=self.blind_mode,
                time_limit=self.time_limit,
                is_custom=False,
                is_drill=True
            )
            Storage.add_record(record)
            engine.show_result(
                rhythm_report=rhythm_report,
                drill_comparison=comparison_bars
            )

    def _draw_multiplayer_menu(self, max_y: int, max_x: int):
        self.stdscr.clear()

        title = "=== 多人竞速对战 ==="
        self.stdscr.addstr(2, (max_x - len(title)) // 2, title,
                          curses.color_pair(COLOR_HIGHLIGHT) | curses.A_BOLD)

        menu_items = [
            "1. 创建房间 (--host)",
            "2. 加入房间 (--join)",
            "0. 返回主菜单"
        ]

        start_y = 6
        for i, item in enumerate(menu_items):
            y = start_y + i * 2
            x = (max_x - len(item)) // 2

            if i == self.selected_idx:
                self.stdscr.addstr(y, x, f"> {item}",
                                  curses.color_pair(COLOR_CURSOR) | curses.A_BOLD)
            else:
                self.stdscr.addstr(y, x, f"  {item}",
                                  curses.color_pair(COLOR_MENU))

        hint = "使用 ↑↓ 选择，回车确认，ESC 返回"
        self.stdscr.addstr(max_y - 2, (max_x - len(hint)) // 2, hint,
                          curses.color_pair(COLOR_PENDING) | curses.A_DIM)

    def _run_multiplayer_menu(self):
        max_y, max_x = self.stdscr.getmaxyx()
        self._draw_multiplayer_menu(max_y, max_x)
        self.stdscr.refresh()

        while True:
            try:
                key = self.stdscr.getch()
            except KeyboardInterrupt:
                break

            if key == 27:
                break
            elif key == curses.KEY_UP:
                self.selected_idx = (self.selected_idx - 1) % 3
            elif key == curses.KEY_DOWN:
                self.selected_idx = (self.selected_idx + 1) % 3
            elif key in (curses.KEY_ENTER, 10, 13):
                if self.selected_idx == 0:
                    self.selected_idx = 0
                    self._run_host_mode()
                    break
                elif self.selected_idx == 1:
                    self.selected_idx = 0
                    self._run_join_mode()
                    break
                elif self.selected_idx == 2:
                    break

            # Redraw the menu
            max_y, max_x = self.stdscr.getmaxyx()
            self._draw_multiplayer_menu(max_y, max_x)
            self.stdscr.refresh()

    def _run_host_mode(self):
        self.server = MultiplayerServer(self.host_port)
        if not self.server.start():
            self.stdscr.clear()
            max_y, max_x = self.stdscr.getmaxyx()
            msg = f"无法启动服务器，端口 {self.host_port} 可能已被占用。"
            self.stdscr.addstr(max_y // 2, (max_x - len(msg)) // 2, msg,
                              curses.color_pair(COLOR_RED))
            self.stdscr.refresh()
            time.sleep(2)
            return

        self.client = MultiplayerClient()
        self.client.connect('127.0.0.1', self.host_port)

        self._run_multiplayer_lobby(is_host=True)

    def _run_join_mode(self):
        if not self.join_addr:
            curses.echo()
            curses.curs_set(1)
            self.stdscr.clear()
            max_y, max_x = self.stdscr.getmaxyx()

            prompt = "请输入服务器地址 (格式: ip:port): "
            self.stdscr.addstr(max_y // 2, 2, prompt, curses.color_pair(COLOR_HIGHLIGHT))
            self.stdscr.refresh()

            addr = ""
            while True:
                key = self.stdscr.getch()
                if key in (curses.KEY_ENTER, 10, 13):
                    break
                elif key == 27:
                    curses.noecho()
                    curses.curs_set(0)
                    return
                elif key in (curses.KEY_BACKSPACE, 8, 127):
                    if addr:
                        addr = addr[:-1]
                        y, x = self.stdscr.getyx()
                        self.stdscr.addstr(y, x - 1, " ")
                        self.stdscr.move(y, x - 1)
                elif 32 <= key <= 126:
                    addr += chr(key)

            curses.noecho()
            curses.curs_set(0)
            self.join_addr = addr

        if ':' not in self.join_addr:
            self.stdscr.clear()
            max_y, max_x = self.stdscr.getmaxyx()
            msg = "地址格式错误，请使用 ip:port 格式。"
            self.stdscr.addstr(max_y // 2, (max_x - len(msg)) // 2, msg,
                              curses.color_pair(COLOR_RED))
            self.stdscr.refresh()
            time.sleep(2)
            return

        host, port_str = self.join_addr.rsplit(':', 1)
        try:
            port = int(port_str)
        except ValueError:
            self.stdscr.clear()
            max_y, max_x = self.stdscr.getmaxyx()
            msg = "端口号格式错误。"
            self.stdscr.addstr(max_y // 2, (max_x - len(msg)) // 2, msg,
                              curses.color_pair(COLOR_RED))
            self.stdscr.refresh()
            time.sleep(2)
            return

        self.client = MultiplayerClient()
        if not self.client.connect(host, port):
            self.stdscr.clear()
            max_y, max_x = self.stdscr.getmaxyx()
            msg = f"无法连接到 {host}:{port}"
            self.stdscr.addstr(max_y // 2, (max_x - len(msg)) // 2, msg,
                              curses.color_pair(COLOR_RED))
            self.stdscr.refresh()
            time.sleep(2)
            return

        self._run_multiplayer_lobby(is_host=False)

    def _run_multiplayer_lobby(self, is_host: bool):
        self.multiplayer_players = []
        self.multiplayer_game_text = ""
        self.multiplayer_started = False
        self.countdown = 0
        ready = False

        def lobby_cb(players, game_text, started):
            self.multiplayer_players = players
            self.multiplayer_game_text = game_text
            self.multiplayer_started = started

        def countdown_cb(seconds):
            self.countdown = seconds

        def start_cb(game_text):
            self.multiplayer_game_text = game_text
            self.multiplayer_started = True

        def progress_cb(players, total_chars):
            self.multiplayer_players = players

        def finish_cb(winner_id, players):
            self.multiplayer_result = {
                'winner_id': winner_id,
                'players': players
            }

        self.client.lobby_callback = lobby_cb
        self.client.countdown_callback = countdown_cb
        self.client.start_callback = start_cb
        self.client.progress_callback = progress_cb
        self.client.finish_callback = finish_cb

        self.stdscr.nodelay(True)

        while True:
            max_y, max_x = self.stdscr.getmaxyx()
            self.stdscr.clear()

            title = "=== 多人竞速大厅 ==="
            self.stdscr.addstr(1, (max_x - len(title)) // 2, title,
                              curses.color_pair(COLOR_HIGHLIGHT) | curses.A_BOLD)

            if self.countdown > 0:
                countdown_msg = f"游戏即将开始: {self.countdown}"
                self.stdscr.addstr(3, (max_x - len(countdown_msg)) // 2, countdown_msg,
                                  curses.color_pair(COLOR_HIGHLIGHT) | curses.A_BOLD)
            elif self.countdown == 0 and self.multiplayer_started:
                break

            y = 6
            header = f"{'玩家':<15}{'状态':<15}"
            self.stdscr.addstr(y, 4, header, curses.color_pair(COLOR_HIGHLIGHT) | curses.A_UNDERLINE)
            y += 2

            for p in self.multiplayer_players:
                name = p.get('name', 'Unknown')[:12]
                is_ready = p.get('ready', False)
                connected = p.get('connected', True)
                is_self = p.get('id') == self.client.player_id

                prefix = "★ " if is_self else "  "
                status = ""
                if not connected:
                    status = "【已断开】"
                    color = COLOR_RED
                elif is_ready:
                    status = "【已准备】"
                    color = COLOR_CORRECT
                else:
                    status = "【等待中】"
                    color = COLOR_PENDING

                line = f"{prefix}{name:<15}{status}"
                self.stdscr.addstr(y, 4, line, curses.color_pair(color))
                y += 1

            y += 1
            if self.multiplayer_players:
                connected = [p for p in self.multiplayer_players if p.get('connected', False)]
                all_ready = all(p.get('ready', False) for p in connected)
                if len(connected) < 2:
                    hint = f"等待更多玩家加入 ({len(connected)}/2-4)"
                    self.stdscr.addstr(y, 4, hint, curses.color_pair(COLOR_PENDING) | curses.A_DIM)
                elif not ready and not all_ready:
                    hint = "按 SPACE 准备/取消准备"
                    self.stdscr.addstr(y, 4, hint, curses.color_pair(COLOR_HIGHLIGHT))
                elif ready:
                    hint = "【已准备】 按 SPACE 取消准备"
                    self.stdscr.addstr(y, 4, hint, curses.color_pair(COLOR_CORRECT))

            if self.multiplayer_game_text:
                y += 2
                self.stdscr.addstr(y, 4, "练习文本预览:", curses.color_pair(COLOR_HIGHLIGHT))
                preview = self.multiplayer_game_text[:80]
                self.stdscr.addstr(y + 1, 6, preview, curses.color_pair(COLOR_PENDING))

            exit_hint = "按 ESC 退出"
            self.stdscr.addstr(max_y - 2, (max_x - len(exit_hint)) // 2, exit_hint,
                              curses.color_pair(COLOR_PENDING) | curses.A_DIM)

            self.stdscr.refresh()

            try:
                key = self.stdscr.getch()
            except KeyboardInterrupt:
                break

            if key == 27:
                break
            elif key == ord(' ') and not self.multiplayer_started and self.countdown == 0:
                ready = not ready
                self.client.send_ready(ready)

            if not self.client.is_connected():
                break

            time.sleep(0.05)

        if self.multiplayer_started and self.multiplayer_game_text:
            self._run_multiplayer_game()

        self.stdscr.nodelay(False)
        if self.client:
            self.client.close()
        if self.server:
            self.server.stop()

    def _run_multiplayer_game(self):
        def progress_cb(pos, wpm):
            if self.client and self.client.is_connected():
                self.client.send_progress(pos, wpm)

        engine = TypingEngine(
            self.stdscr, self.multiplayer_game_text,
            self.blind_mode, self.time_limit,
            progress_callback=progress_cb,
            opponent_data=self.multiplayer_players
        )

        def opponent_update_thread():
            while not engine.finished and not engine.quit_early:
                time.sleep(0.1)
                engine.opponent_data = list(self.multiplayer_players)

        threading.Thread(target=opponent_update_thread, daemon=True).start()

        stats = engine.run()
        stats.__dict__['player_id'] = self.client.player_id

        if not engine.quit_early and stats.total_chars > 0:
            stats_dict = {
                'wpm': stats.wpm,
                'accuracy': stats.accuracy,
                'total_chars': stats.total_chars,
                'correct_chars': stats.correct_chars,
                'wrong_chars': stats.wrong_chars,
                'duration': stats.elapsed_time,
                'rhythm_score': stats.rhythm_score
            }
            self.client.send_finish(stats_dict)

            while not self.multiplayer_result and self.client.is_connected():
                time.sleep(0.1)

            rhythm_report = RhythmVisualizer.generate_rhythm_report(stats, width=60)

            record = Storage.create_record_from_stats(
                stats,
                course_id=None,
                course_name="多人竞速",
                blind_mode=self.blind_mode,
                time_limit=self.time_limit,
                is_custom=False
            )
            Storage.add_record(record)
            engine.show_result(
                rhythm_report=rhythm_report,
                multiplayer_result=self.multiplayer_result
            )

    def _run_rhythm_history(self):
        history = Storage.get_recent_rhythm(10)
        chart_lines = RhythmVisualizer.generate_rhythm_history_chart(
            history, width=60, height=12
        )

        max_y, max_x = self.stdscr.getmaxyx()
        self.stdscr.clear()

        y = 1
        for line in chart_lines:
            if y >= max_y - 2:
                break
            x = max(2, (max_x - len(line)) // 2)

            if line.startswith("=") or line.startswith("📊"):
                attr = curses.color_pair(COLOR_HIGHLIGHT) | curses.A_BOLD
            elif "ms │" in line:
                parts = line.split("│", 1)
                if len(parts) == 2:
                    self.stdscr.addstr(y, 2, parts[0] + "│",
                                      curses.color_pair(COLOR_PENDING) | curses.A_DIM)
                    plot_part = parts[1]
                    x_pos = 2 + len(parts[0]) + 1
                    for ci, ch in enumerate(plot_part):
                        if ch in ('·', '●', '█', '░', '─', '└'):
                            self.stdscr.addstr(y, x_pos + ci, ch,
                                              curses.color_pair(COLOR_MENU))
                        else:
                            self.stdscr.addstr(y, x_pos + ci, ch)
                    y += 1
                    continue
                attr = curses.color_pair(COLOR_PENDING)
            elif "平均:" in line or "最佳:" in line:
                attr = curses.color_pair(COLOR_HIGHLIGHT)
            else:
                attr = curses.color_pair(COLOR_PENDING)

            try:
                self.stdscr.addstr(y, x, line[:max_x - 4], attr)
            except curses.error:
                pass
            y += 1

        prompt = "按任意键返回..."
        self.stdscr.addstr(max_y - 2, (max_x - len(prompt)) // 2, prompt,
                          curses.color_pair(COLOR_PENDING) | curses.A_DIM)
        self.stdscr.refresh()
        self.stdscr.getch()
