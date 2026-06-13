#!/usr/bin/env python3
"""终端打字训练 CLI 工具 - 入口文件"""

import sys
import curses

from typing_trainer.cli import TypingTrainerCLI


def main():
    try:
        curses.wrapper(_run_app)
    except KeyboardInterrupt:
        print("\n再见！感谢使用终端打字训练工具。")
        sys.exit(0)


def _run_app(stdscr):
    app = TypingTrainerCLI(stdscr)
    app.run()


if __name__ == "__main__":
    main()
