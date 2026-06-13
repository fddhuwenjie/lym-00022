import math
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass

from .stats import TypingStats
from .config import RHYTHM_PAUSE_THRESHOLD_MS, RHYTHM_SECTION_SIZE
from .visualizer import ChartData, ASCIIChart


@dataclass
class RhythmAnalysis:
    rhythm_score: float
    avg_interval_ms: float
    max_interval_ms: float
    min_interval_ms: float
    stdev_interval_ms: float
    pause_count: int
    section_stdevs: List[Tuple[int, float]]


class RhythmVisualizer:
    @staticmethod
    def analyze(stats: TypingStats) -> RhythmAnalysis:
        intervals = stats.inter_keystroke_intervals

        if not intervals:
            return RhythmAnalysis(0, 0, 0, 0, 0, 0, [])

        intervals_ms = [i * 1000 for i in intervals]

        avg = sum(intervals_ms) / len(intervals_ms)
        max_i = max(intervals_ms)
        min_i = min(intervals_ms)

        variance = sum((x - avg) ** 2 for x in intervals_ms) / len(intervals_ms)
        stdev = math.sqrt(variance)

        pause_count = sum(1 for x in intervals_ms if x > RHYTHM_PAUSE_THRESHOLD_MS)

        section_stdevs = stats.calculate_section_stdevs(RHYTHM_SECTION_SIZE)
        rhythm_score = stats.calculate_rhythm_score()

        return RhythmAnalysis(
            rhythm_score=rhythm_score,
            avg_interval_ms=avg,
            max_interval_ms=max_i,
            min_interval_ms=min_i,
            stdev_interval_ms=stdev,
            pause_count=pause_count,
            section_stdevs=section_stdevs
        )

    @staticmethod
    def generate_scatter_plot(
        intervals: List[float],
        width: int = 60,
        height: int = 10,
        threshold_ms: int = RHYTHM_PAUSE_THRESHOLD_MS
    ) -> List[str]:
        if not intervals:
            return ["(无节奏数据)"]

        intervals_ms = [i * 1000 for i in intervals]

        num_points = min(len(intervals_ms), width - 8)
        step = max(1, len(intervals_ms) // num_points)

        sampled = intervals_ms[::step]
        if len(sampled) > num_points:
            sampled = sampled[:num_points]

        max_val = max(max(sampled), threshold_ms * 1.2)
        min_val = 0

        if max_val == min_val:
            max_val = min_val + 1

        plot_height = height
        plot_width = len(sampled)

        grid = [[' ' for _ in range(plot_width + 8)] for _ in range(plot_height)]

        threshold_y = int(round((plot_height - 1) * (1 - threshold_ms / max_val)))
        threshold_y = max(0, min(plot_height - 1, threshold_y))
        for x in range(plot_width):
            if grid[threshold_y][x + 7] == ' ':
                grid[threshold_y][x + 7] = '-'

        points = []
        for i, val in enumerate(sampled):
            normalized = (val - min_val) / (max_val - min_val) if max_val > min_val else 0
            y = int(round((plot_height - 1) * (1 - normalized)))
            y = max(0, min(plot_height - 1, y))
            points.append((i, y, val))
            is_hot = val > threshold_ms

            char = '●' if is_hot else '·'
            if grid[y][i + 7] in (' ', '-'):
                grid[y][i + 7] = char

        result = []
        result.append("=== 击键间隔散点图 ===")
        result.append("")
        result.append(f"阈值线: {threshold_ms}ms (超过标记为红色 ●)")
        result.append("")

        for row_idx in range(plot_height):
            y_val = max_val - (row_idx / (plot_height - 1)) * (max_val - min_val) if plot_height > 1 else max_val

            if row_idx == 0 or row_idx == plot_height - 1 or row_idx == threshold_y:
                y_label = f"{y_val:5.0f}ms │"
            else:
                y_label = "        │"

            line = y_label
            for col_idx in range(plot_width):
                char = grid[row_idx][col_idx + 7]
                line += char
            result.append(line)

        x_axis = "        └" + "─" * plot_width
        result.append(x_axis)

        x_labels = "         "
        label_step = max(1, len(sampled) // 10)
        for i in range(len(sampled)):
            if i % label_step == 0:
                x_labels += f"{i * step + 1:<3}"
            else:
                x_labels += "   "
        result.append(x_labels[:plot_width + 9])
        result.append("         " + "字符序号 →")

        return result

    @staticmethod
    def generate_stability_chart(
        section_stdevs: List[Tuple[int, float]],
        width: int = 60,
        height: int = 6
    ) -> List[str]:
        if not section_stdevs:
            return ["(稳定性数据不足)"]

        values = [std * 1000 for _, std in section_stdevs]
        labels = [f"#{i + 1}" for i, _ in section_stdevs]

        data = ChartData(label="标准差(ms)", values=values, labels=labels)
        chart = ASCIIChart.line_chart(
            data, width=width, height=height,
            title="节奏稳定度 (每 20 字符标准差)"
        )

        return chart

    @staticmethod
    def generate_rhythm_report(
        stats: TypingStats,
        width: int = 60
    ) -> List[str]:
        analysis = RhythmVisualizer.analyze(stats)

        lines = []
        lines.append("")
        lines.append("=" * width)
        lines.append("🎵 节奏分析报告")
        lines.append("=" * width)
        lines.append("")

        lines.append(f"节奏评分: {analysis.rhythm_score:.1f} / 100")
        lines.append("")

        if analysis.rhythm_score >= 80:
            rating = "优秀 - 节奏非常稳定！"
        elif analysis.rhythm_score >= 60:
            rating = "良好 - 节奏比较稳定"
        elif analysis.rhythm_score >= 40:
            rating = "一般 - 还有提升空间"
        else:
            rating = "需加强 - 注意保持均匀节奏"

        lines.append(f"评价: {rating}")
        lines.append("")

        lines.append(f"平均击键间隔: {analysis.avg_interval_ms:.1f} ms")
        lines.append(f"最快击键: {analysis.min_interval_ms:.1f} ms")
        lines.append(f"最慢击键: {analysis.max_interval_ms:.1f} ms")
        lines.append(f"间隔标准差: {analysis.stdev_interval_ms:.1f} ms")
        lines.append(f"超过 {RHYTHM_PAUSE_THRESHOLD_MS}ms 停顿: {analysis.pause_count} 次")
        lines.append("")

        scatter = RhythmVisualizer.generate_scatter_plot(
            stats.inter_keystroke_intervals,
            width=width,
            height=10
        )
        lines.extend(scatter)
        lines.append("")

        if analysis.section_stdevs:
            stability = RhythmVisualizer.generate_stability_chart(
                analysis.section_stdevs,
                width=width,
                height=6
            )
            lines.extend(stability)
            lines.append("")

        return lines

    @staticmethod
    def generate_rhythm_history_chart(
        history: List[Dict],
        width: int = 60,
        height: int = 12
    ) -> List[str]:
        if not history:
            return ["(暂无节奏历史记录)"]

        history_sorted = sorted(history, key=lambda x: x['timestamp'])
        recent = history_sorted[-10:]

        scores = [h['rhythm_score'] for h in recent]
        labels = [f"#{i + 1}" for i in range(len(recent))]

        data = ChartData(label="节奏评分", values=scores, labels=labels)
        chart = ASCIIChart.line_chart(
            data, width=width, height=height,
            title="最近 10 次练习节奏评分趋势"
        )

        lines = []
        lines.append("")
        lines.append("=" * width)
        lines.append("📊 节奏评分历史")
        lines.append("=" * width)
        lines.append("")
        lines.extend(chart)

        if len(recent) >= 2:
            avg = sum(scores) / len(scores)
            best = max(scores)
            worst = min(scores)
            trend = scores[-1] - scores[0]
            trend_sign = '+' if trend >= 0 else ''

            lines.append("")
            lines.append(f"平均: {avg:.1f}  |  最佳: {best:.1f}  |  最低: {worst:.1f}  |  趋势: {trend_sign}{trend:.1f}")

        return lines
