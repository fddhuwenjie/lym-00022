#!/usr/bin/env python3
"""终端打字训练 CLI 工具 - 入口文件"""

import sys
import argparse
import curses

from typing_trainer.cli import TypingTrainerCLI
from typing_trainer.config import DEFAULT_MULTIPLAYER_PORT


def parse_args():
    parser = argparse.ArgumentParser(
        description="终端打字训练工具 - 支持多人对战、智能薄弱训练和节奏可视化"
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '--host',
        type=int,
        nargs='?',
        const=DEFAULT_MULTIPLAYER_PORT,
        metavar='PORT',
        help=f'创建多人对战房间，监听指定端口 (默认: {DEFAULT_MULTIPLAYER_PORT})'
    )
    group.add_argument(
        '--join',
        type=str,
        metavar='IP:PORT',
        help='加入多人对战房间，指定服务器地址 (如: 192.168.1.100:54321)'
    )
    group.add_argument(
        '--drill',
        action='store_true',
        help='启动专项薄弱训练模式，根据历史错字自动生成练习'
    )
    group.add_argument(
        '--rhythm-history',
        action='store_true',
        help='查看最近 10 次练习的节奏评分趋势'
    )

    return parser.parse_args()


def main():
    args = parse_args()

    mode = "normal"
    host_port = DEFAULT_MULTIPLAYER_PORT
    join_addr = None

    if args.host is not None:
        mode = "host"
        host_port = args.host
    elif args.join is not None:
        mode = "join"
        join_addr = args.join
    elif args.drill:
        mode = "drill"
    elif args.rhythm_history:
        mode = "rhythm_history"

    try:
        curses.wrapper(_run_app, mode, host_port, join_addr)
    except KeyboardInterrupt:
        print("\n再见！感谢使用终端打字训练工具。")
        sys.exit(0)


def _run_app(stdscr, mode, host_port, join_addr):
    app = TypingTrainerCLI(
        stdscr,
        mode=mode,
        host_port=host_port,
        join_addr=join_addr
    )
    app.run()


if __name__ == "__main__":
    main()
