from typing import List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ChartData:
    label: str
    values: List[float]
    labels: List[str]


class ASCIIChart:
    @staticmethod
    def line_chart(
        data: ChartData,
        width: int = 60,
        height: int = 15,
        title: str = ""
    ) -> List[str]:
        if not data.values:
            return ["(无数据)"]
        
        values = data.values
        labels = data.labels
        
        min_val = min(values)
        max_val = max(values)
        
        if min_val == max_val:
            max_val = min_val + 1
        
        value_range = max_val - min_val
        
        num_points = min(len(values), width - 10)
        step = max(1, len(values) // num_points)
        
        sampled_values = values[::step]
        sampled_labels = labels[::step]
        
        if len(sampled_values) > num_points:
            sampled_values = sampled_values[:num_points]
            sampled_labels = sampled_labels[:num_points]
        
        chart_height = height - 3
        chart_width = min(len(sampled_values), width - 10)
        
        plot = [[' ' for _ in range(chart_width + 8)] for _ in range(chart_height)]
        
        points = []
        for i, val in enumerate(sampled_values[:chart_width]):
            normalized = (val - min_val) / value_range
            y = int(round((chart_height - 1) * (1 - normalized)))
            y = max(0, min(chart_height - 1, y))
            points.append((i, y, val))
        
        for i in range(len(points) - 1):
            x1, y1, _ = points[i]
            x2, y2, _ = points[i + 1]
            
            if x1 == x2:
                continue
            
            steps = max(abs(x2 - x1), abs(y2 - y1))
            for s in range(steps + 1):
                t = s / steps if steps > 0 else 0
                x = int(round(x1 + (x2 - x1) * t))
                y = int(round(y1 + (y2 - y1) * t))
                if 0 <= x < chart_width and 0 <= y < chart_height:
                    plot[y][x + 7] = '·'
        
        for x, y, val in points:
            if 0 <= x < chart_width and 0 <= y < chart_height:
                plot[y][x + 7] = '●'
        
        result = []
        
        if title:
            result.append(title)
            result.append('')
        
        for row_idx, row in enumerate(plot):
            y_val = max_val - (row_idx / (chart_height - 1)) * value_range if chart_height > 1 else max_val
            
            if row_idx == 0 or row_idx == chart_height - 1 or row_idx == chart_height // 2:
                y_label = f"{y_val:5.1f} │"
            else:
                y_label = "      │"
            
            result.append(y_label + ''.join(row[7:7 + chart_width]))
        
        x_axis = "      └" + "─" * chart_width
        result.append(x_axis)
        
        x_labels = "       "
        label_step = max(1, len(sampled_labels) // 8)
        for i, label in enumerate(sampled_labels[:chart_width]):
            if i % label_step == 0:
                short_label = label[:4]
                x_labels += short_label
            else:
                x_labels += ' '
        
        result.append(x_labels[:chart_width + 7])
        
        result.append('')
        result.append(f"图例: {data.label}")
        
        return result

    @staticmethod
    def bar_chart(
        items: List[Tuple[str, float]],
        width: int = 50,
        title: str = ""
    ) -> List[str]:
        if not items:
            return ["(无数据)"]
        
        result = []
        if title:
            result.append(title)
            result.append('')
        
        max_val = max(v for _, v in items)
        max_label_len = max(len(l) for l, _ in items)
        
        bar_max_width = width - max_label_len - 5
        
        for label, value in items:
            bar_width = int((value / max_val) * bar_max_width) if max_val > 0 else 0
            bar = '#' * bar_width
            line = f"{label.ljust(max_label_len)} | {bar} {value:.1f}"
            result.append(line)
        
        return result

    @staticmethod
    def progress_bar(
        current: float,
        total: float,
        width: int = 30,
        show_percent: bool = True
    ) -> str:
        if total <= 0:
            percent = 0
        else:
            percent = min(100, (current / total) * 100)
        
        filled = int((percent / 100) * width)
        bar = '#' * filled + '-' * (width - filled)
        
        if show_percent:
            return f"[{bar}] {percent:.1f}%"
        return f"[{bar}]"

    @staticmethod
    def format_stats_summary(records, max_width: int = 60) -> List[str]:
        if not records:
            return ["暂无历史记录"]
        
        result = []
        
        total_sessions = len(records)
        avg_wpm = sum(r.wpm for r in records) / total_sessions if total_sessions > 0 else 0
        avg_accuracy = sum(r.accuracy for r in records) / total_sessions if total_sessions > 0 else 0
        best_wpm = max(r.wpm for r in records)
        best_accuracy = max(r.accuracy for r in records)
        
        result.append("=== 统计概要 ===")
        result.append(f"总训练次数: {total_sessions}")
        result.append(f"平均 WPM: {avg_wpm:.2f}")
        result.append(f"平均准确率: {avg_accuracy:.2f}%")
        result.append(f"最佳 WPM: {best_wpm:.2f}")
        result.append(f"最佳准确率: {best_accuracy:.2f}%")
        result.append('')
        
        recent = records[-10:] if len(records) > 10 else records
        if recent:
            wpm_values = [r.wpm for r in recent]
            wpm_labels = [f"#{i+1}" for i in range(len(recent))]
            
            chart_data = ChartData(label="WPM", values=wpm_values, labels=wpm_labels)
            chart_lines = ASCIIChart.line_chart(
                chart_data,
                width=max_width,
                height=10,
                title="最近 10 次 WPM 趋势"
            )
            result.extend(chart_lines)
        
        return result
