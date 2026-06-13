"""简单的功能测试 - 验证非 UI 模块"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing_trainer.courses import list_courses, get_course
from typing_trainer.stats import TypingStats
from typing_trainer.storage import Storage, Record
from typing_trainer.visualizer import ASCIIChart, ChartData
import time


def test_courses():
    print("=" * 50)
    print("测试课程模块...")
    courses = list_courses()
    print(f"  课程数量: {len(courses)}")
    
    for course in courses:
        print(f"  - [{course.id}] {course.name} (难度 {course.difficulty})")
        print(f"    描述: {course.description}")
        print(f"    文本数: {len(course.texts)}")
    
    assert len(courses) >= 6, "至少需要 6 套课程"
    print("  [OK] 课程模块测试通过")


def test_stats():
    print("\n" + "=" * 50)
    print("测试统计模块...")
    
    stats = TypingStats()
    stats.start()
    time.sleep(0.01)
    
    chars = "hello world"
    for char in chars:
        stats.record_correct(char, 0.1)
    
    stats.record_wrong('x', 'e', 0.2)
    stats.record_wrong('z', 'd', 0.3)
    stats.record_wrong('x', 'e', 0.15)
    
    stats.end()
    
    print(f"  总字符: {stats.total_chars}")
    print(f"  正确: {stats.correct_chars}")
    print(f"  错误: {stats.wrong_chars}")
    print(f"  准确率: {stats.accuracy:.2f}%")
    print(f"  WPM: {stats.wpm:.2f}")
    print(f"  用时: {stats.elapsed_time:.4f}s")
    
    top_errors = stats.top_errors(3)
    print(f"  最常错字符: {top_errors}")
    
    slowest = stats.slowest_chars(3)
    print(f"  最慢字符: {slowest}")
    
    assert stats.total_chars == 14, f"期望 14，实际 {stats.total_chars}"
    assert stats.wrong_chars == 3, f"期望 3，实际 {stats.wrong_chars}"
    print("  [OK] 统计模块测试通过")


def test_visualizer():
    print("\n" + "=" * 50)
    print("测试可视化模块...")
    
    values = [25, 30, 28, 35, 40, 38, 45, 50, 48, 55]
    labels = [f"#{i+1}" for i in range(len(values))]
    
    chart_data = ChartData(label="WPM", values=values, labels=labels)
    chart = ASCIIChart.line_chart(chart_data, width=50, height=10, title="WPM 趋势")
    
    print("  ASCII 折线图:")
    for line in chart:
        print(f"    {line}")
    
    bar_items = [
        ("字母a", 12),
        ("字母b", 8),
        ("字母c", 15),
        ("字母d", 5),
        ("字母e", 20),
    ]
    bar_chart = ASCIIChart.bar_chart(bar_items, width=40, title="错字分布")
    print("\n  ASCII 柱状图:")
    for line in bar_chart:
        print(f"    {line}")
    
    progress = ASCIIChart.progress_bar(75, 100, width=30)
    print(f"\n  进度条: {progress}")
    
    print("  [OK] 可视化模块测试通过")


def test_storage():
    print("\n" + "=" * 50)
    print("测试存储模块...")
    
    from typing_trainer.config import RECORDS_FILE, CUSTOM_TEXT_FILE
    
    records = Storage.get_all_records()
    print(f"  历史记录数: {len(records)}")
    
    custom_texts = Storage.get_all_custom_texts()
    print(f"  自定义文本数: {len(custom_texts)}")
    
    best = Storage.get_best_wpm()
    if best:
        print(f"  最佳 WPM: {best.wpm:.2f} ({best.course_name})")
    
    print("  [OK] 存储模块测试通过")


def main():
    print("终端打字训练工具 - 功能测试")
    print("=" * 50)
    
    try:
        test_courses()
        test_stats()
        test_visualizer()
        test_storage()
        
        print("\n" + "=" * 50)
        print("[SUCCESS] 所有测试通过！")
        return 0
    except AssertionError as e:
        print(f"\n[FAIL] 测试失败: {e}")
        return 1
    except Exception as e:
        print(f"\n[ERROR] 发生错误: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
