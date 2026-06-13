import curses
import random
from typing import Optional
from .courses import list_courses, get_course, Lesson
from .typing_engine import TypingEngine
from .storage import Storage, Record, CustomText
from .visualizer import ASCIIChart, ChartData
from .config import (
    COLOR_CORRECT, COLOR_WRONG, COLOR_CURSOR, COLOR_PENDING,
    COLOR_HIGHLIGHT, COLOR_MENU, DIFFICULTY_LEVELS
)


class TypingTrainerCLI:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.blind_mode = False
        self.time_limit: Optional[int] = None
        self.current_menu = "main"
        self.selected_idx = 0
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

    def run(self):
        curses.curs_set(0)
        self.stdscr.keypad(True)
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
            "3. 历史记录",
            "4. 进步曲线",
            "5. 设置选项",
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
        
        menu_items = 6
        
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
                self.current_menu = "history"
                self.selected_idx = 0
            elif self.selected_idx == 3:
                self.current_menu = "progress"
                self.selected_idx = 0
            elif self.selected_idx == 4:
                self.current_menu = "settings"
                self.selected_idx = 0
            elif self.selected_idx == 5:
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
            record = Storage.create_record_from_stats(
                stats,
                course_id=course.id,
                course_name=course.name,
                blind_mode=self.blind_mode,
                time_limit=self.time_limit,
                is_custom=False
            )
            Storage.add_record(record)
            engine.show_result()

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
                record = Storage.create_record_from_stats(
                    stats,
                    course_id=None,
                    course_name="临时练习",
                    blind_mode=self.blind_mode,
                    time_limit=self.time_limit,
                    is_custom=True
                )
                Storage.add_record(record)
                engine.show_result()

    def _start_custom_practice(self, ct: CustomText):
        engine = TypingEngine(self.stdscr, ct.content, self.blind_mode, self.time_limit)
        stats = engine.run()
        
        if not engine.quit_early and stats.total_chars > 0:
            record = Storage.create_record_from_stats(
                stats,
                course_id=None,
                course_name=ct.name,
                blind_mode=self.blind_mode,
                time_limit=self.time_limit,
                is_custom=True
            )
            Storage.add_record(record)
            engine.show_result()

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
