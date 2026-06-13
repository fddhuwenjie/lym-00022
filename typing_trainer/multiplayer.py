import socket
import json
import time
import threading
import uuid
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Callable, Tuple
from collections import deque
import random

from .config import (
    DEFAULT_MULTIPLAYER_PORT, MAX_MULTIPLAYER_PLAYERS,
    MULTIPLAYER_COUNTDOWN_SECONDS, NETWORK_TIMEOUT,
    SERVER_POLL_INTERVAL, CLIENT_POLL_INTERVAL,
    MSG_TYPE_HELLO, MSG_TYPE_LOBBY_UPDATE, MSG_TYPE_READY,
    MSG_TYPE_COUNTDOWN, MSG_TYPE_START, MSG_TYPE_PROGRESS,
    MSG_TYPE_FINISH, MSG_TYPE_DISCONNECT
)
from .courses import COURSES


@dataclass
class Player:
    id: str
    name: str
    addr: Tuple[str, int]
    ready: bool = False
    connected: bool = True
    current_pos: int = 0
    wpm: float = 0.0
    finished: bool = False
    finish_time: Optional[float] = None
    final_stats: Optional[Dict] = None
    forfeit: bool = False


@dataclass
class MultiplayerState:
    game_text: str = ""
    countdown: int = 0
    started: bool = False
    finished: bool = False
    winner_id: Optional[str] = None
    start_time: float = 0


class Message:
    def __init__(self, msg_type: str, data: Dict = None):
        self.type = msg_type
        self.data = data or {}

    def to_bytes(self) -> bytes:
        msg = json.dumps({"type": self.type, "data": self.data})
        return (msg + "\n").encode('utf-8')

    @staticmethod
    def from_bytes(data: bytes) -> Optional['Message']:
        try:
            text = data.decode('utf-8').strip()
            if not text:
                return None
            parsed = json.loads(text)
            return Message(parsed.get("type", ""), parsed.get("data", {}))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return None


class MultiplayerServer:
    def __init__(self, port: int = DEFAULT_MULTIPLAYER_PORT):
        self.port = port
        self.players: Dict[str, Player] = {}
        self.state = MultiplayerState()
        self.server_sock: Optional[socket.socket] = None
        self.running = False
        self.client_threads: Dict[str, threading.Thread] = {}
        self.client_socks: Dict[str, socket.socket] = {}
        self.send_buffers: Dict[str, deque] = {}
        self.recv_buffers: Dict[str, deque] = {}
        self.lock = threading.Lock()
        self.game_start_callback: Optional[Callable] = None
        self.game_finish_callback: Optional[Callable] = None
        self._select_game_text()

    def _select_game_text(self):
        course = random.choice(COURSES)
        self.state.game_text = random.choice(course.texts)

    def start(self) -> bool:
        try:
            self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_sock.bind(('0.0.0.0', self.port))
            self.server_sock.listen(MAX_MULTIPLAYER_PLAYERS)
            self.server_sock.settimeout(NETWORK_TIMEOUT)
            self.running = True

            accept_thread = threading.Thread(target=self._accept_loop, daemon=True)
            accept_thread.start()

            poll_thread = threading.Thread(target=self._poll_loop, daemon=True)
            poll_thread.start()

            return True
        except OSError:
            return False

    def _accept_loop(self):
        while self.running:
            try:
                client_sock, addr = self.server_sock.accept()
                client_sock.settimeout(NETWORK_TIMEOUT)

                player_id = str(uuid.uuid4())[:8]

                with self.lock:
                    if len(self.players) >= MAX_MULTIPLAYER_PLAYERS:
                        client_sock.close()
                        continue

                    player = Player(
                        id=player_id,
                        name=f"Player{len(self.players) + 1}",
                        addr=addr
                    )
                    self.players[player_id] = player
                    self.client_socks[player_id] = client_sock
                    self.send_buffers[player_id] = deque()
                    self.recv_buffers[player_id] = deque()

                client_thread = threading.Thread(
                    target=self._client_loop,
                    args=(player_id,),
                    daemon=True
                )
                self.client_threads[player_id] = client_thread
                client_thread.start()

                self._send_to(player_id, Message(MSG_TYPE_HELLO, {
                    'player_id': player_id,
                    'player_name': player.name,
                    'game_text': self.state.game_text
                }))
                self._broadcast_lobby_update()

            except socket.timeout:
                continue
            except OSError:
                if self.running:
                    break

    def _client_loop(self, player_id: str):
        sock = self.client_socks.get(player_id)
        if not sock:
            return

        buffer = b""
        while self.running and self.players.get(player_id, Player(id="", name="", addr=("", 0))).connected:
            try:
                data = sock.recv(4096)
                if not data:
                    break

                buffer += data
                while b"\n" in buffer:
                    line, buffer = buffer.split(b"\n", 1)
                    msg = Message.from_bytes(line)
                    if msg:
                        with self.lock:
                            self.recv_buffers[player_id].append(msg)

            except socket.timeout:
                continue
            except OSError:
                break

        with self.lock:
            if player_id in self.players:
                self.players[player_id].connected = False
                self.players[player_id].forfeit = True
                if not self.state.finished and self.state.started:
                    self.players[player_id].finished = True
            if player_id in self.client_socks:
                try:
                    self.client_socks[player_id].close()
                except OSError:
                    pass
                del self.client_socks[player_id]

        self._broadcast_lobby_update()
        self._check_game_finish()

    def _poll_loop(self):
        while self.running:
            with self.lock:
                for player_id in list(self.players.keys()):
                    player = self.players[player_id]
                    if not player.connected:
                        continue

                    while self.recv_buffers[player_id]:
                        msg = self.recv_buffers[player_id].popleft()
                        self._handle_message(player_id, msg)

                    while self.send_buffers[player_id]:
                        msg = self.send_buffers[player_id][0]
                        try:
                            self.client_socks[player_id].sendall(msg.to_bytes())
                            self.send_buffers[player_id].popleft()
                        except OSError:
                            player.connected = False
                            player.forfeit = True
                            if not self.state.finished and self.state.started:
                                player.finished = True
                            break

            time.sleep(SERVER_POLL_INTERVAL)

    def _handle_message(self, player_id: str, msg: Message):
        player = self.players.get(player_id)
        if not player:
            return

        if msg.type == MSG_TYPE_READY:
            if not self.state.started:
                player.ready = msg.data.get('ready', True)
                self._broadcast_lobby_update()
                self._check_all_ready()

        elif msg.type == MSG_TYPE_PROGRESS:
            if self.state.started and not self.state.finished:
                player.current_pos = msg.data.get('pos', 0)
                player.wpm = msg.data.get('wpm', 0.0)
                self._broadcast_progress()

        elif msg.type == MSG_TYPE_FINISH:
            if self.state.started and not player.finished:
                player.finished = True
                player.finish_time = time.time() - self.state.start_time
                player.final_stats = msg.data.get('stats', {})
                self._broadcast_progress()
                self._check_game_finish()

    def _send_to(self, player_id: str, msg: Message):
        if player_id in self.send_buffers:
            self.send_buffers[player_id].append(msg)

    def _broadcast(self, msg: Message):
        for player_id in self.players:
            if self.players[player_id].connected:
                self._send_to(player_id, msg)

    def _broadcast_lobby_update(self):
        players_data = []
        for pid, player in self.players.items():
            players_data.append({
                'id': pid,
                'name': player.name,
                'ready': player.ready,
                'connected': player.connected,
                'forfeit': player.forfeit
            })
        self._broadcast(Message(MSG_TYPE_LOBBY_UPDATE, {
            'players': players_data,
            'game_text': self.state.game_text,
            'started': self.state.started
        }))

    def _broadcast_progress(self):
        players_data = []
        for pid, player in self.players.items():
            players_data.append({
                'id': pid,
                'name': player.name,
                'pos': player.current_pos,
                'wpm': player.wpm,
                'finished': player.finished,
                'forfeit': player.forfeit,
                'finish_time': player.finish_time,
                'final_stats': player.final_stats
            })
        self._broadcast(Message(MSG_TYPE_PROGRESS, {
            'players': players_data,
            'total_chars': len(self.state.game_text)
        }))

    def _check_all_ready(self):
        if len(self.players) < 2:
            return
        connected_players = [p for p in self.players.values() if p.connected]
        if len(connected_players) < 2:
            return
        all_ready = all(p.ready for p in connected_players)
        if all_ready:
            self._start_countdown()

    def _start_countdown(self):
        self.state.countdown = MULTIPLAYER_COUNTDOWN_SECONDS
        self._broadcast(Message(MSG_TYPE_COUNTDOWN, {'seconds': self.state.countdown}))

        def countdown_thread():
            for i in range(MULTIPLAYER_COUNTDOWN_SECONDS - 1, -1, -1):
                time.sleep(1)
                if not self.running:
                    return
                with self.lock:
                    self.state.countdown = i
                    self._broadcast(Message(MSG_TYPE_COUNTDOWN, {'seconds': i}))
            with self.lock:
                self._start_game()

        threading.Thread(target=countdown_thread, daemon=True).start()

    def _start_game(self):
        self.state.started = True
        self.state.start_time = time.time()
        self.state.finished = False
        self.state.winner_id = None

        for player in self.players.values():
            player.current_pos = 0
            player.wpm = 0.0
            player.finished = False
            player.finish_time = None
            player.final_stats = None

        self._broadcast(Message(MSG_TYPE_START, {
            'game_text': self.state.game_text,
            'start_time': self.state.start_time
        }))

        if self.game_start_callback:
            self.game_start_callback(self.state.game_text)

    def _check_game_finish(self):
        if not self.state.started or self.state.finished:
            return

        finished_players = [p for p in self.players.values() if p.finished]
        connected_players = [p for p in self.players.values() if p.connected]

        if len(finished_players) == len(connected_players) and len(connected_players) >= 2:
            self.state.finished = True

            non_forfeit = [p for p in finished_players if not p.forfeit and p.finish_time is not None]
            if non_forfeit:
                winner = min(non_forfeit, key=lambda p: p.finish_time)
                self.state.winner_id = winner.id

            self._broadcast(Message(MSG_TYPE_FINISH, {
                'winner_id': self.state.winner_id,
                'players': [
                    {
                        'id': p.id,
                        'name': p.name,
                        'finish_time': p.finish_time,
                        'forfeit': p.forfeit,
                        'final_stats': p.final_stats
                    }
                    for p in self.players.values()
                ]
            }))

            if self.game_finish_callback:
                self.game_finish_callback(self.state)

    def get_players(self) -> List[Player]:
        with self.lock:
            return list(self.players.values())

    def stop(self):
        self.running = False
        with self.lock:
            for sock in self.client_socks.values():
                try:
                    sock.close()
                except OSError:
                    pass
            self.client_socks.clear()
            if self.server_sock:
                try:
                    self.server_sock.close()
                except OSError:
                    pass
                self.server_sock = None


class MultiplayerClient:
    def __init__(self):
        self.sock: Optional[socket.socket] = None
        self.player_id: str = ""
        self.player_name: str = ""
        self.game_text: str = ""
        self.players: List[Dict] = []
        self.total_chars: int = 0
        self.countdown: int = 0
        self.started: bool = False
        self.finished: bool = False
        self.winner_id: Optional[str] = None
        self.running = False
        self.send_buffer: deque = deque()
        self.recv_buffer: deque = deque()
        self.lock = threading.Lock()
        self.poll_thread: Optional[threading.Thread] = None
        self.countdown_callback: Optional[Callable[[int], None]] = None
        self.start_callback: Optional[Callable[[str], None]] = None
        self.progress_callback: Optional[Callable[[List[Dict], int], None]] = None
        self.finish_callback: Optional[Callable[[Optional[str], List[Dict]], None]] = None
        self.lobby_callback: Optional[Callable[[List[Dict], str, bool], None]] = None

    def connect(self, host: str, port: int) -> bool:
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(NETWORK_TIMEOUT)
            self.sock.connect((host, port))
            self.running = True

            self.poll_thread = threading.Thread(target=self._poll_loop, daemon=True)
            self.poll_thread.start()

            return True
        except OSError:
            return False

    def _poll_loop(self):
        buffer = b""
        while self.running:
            try:
                with self.lock:
                    while self.send_buffer:
                        msg = self.send_buffer[0]
                        try:
                            self.sock.sendall(msg.to_bytes())
                            self.send_buffer.popleft()
                        except OSError:
                            self.running = False
                            break

                try:
                    data = self.sock.recv(4096)
                    if not data:
                        break

                    buffer += data
                    while b"\n" in buffer:
                        line, buffer = buffer.split(b"\n", 1)
                        msg = Message.from_bytes(line)
                        if msg:
                            with self.lock:
                                self.recv_buffer.append(msg)
                                self._handle_message(msg)

                except socket.timeout:
                    continue
                except OSError:
                    break

            except Exception:
                break

        self.running = False

    def _handle_message(self, msg: Message):
        if msg.type == MSG_TYPE_HELLO:
            self.player_id = msg.data.get('player_id', '')
            self.player_name = msg.data.get('player_name', '')
            self.game_text = msg.data.get('game_text', '')

        elif msg.type == MSG_TYPE_LOBBY_UPDATE:
            self.players = msg.data.get('players', [])
            self.game_text = msg.data.get('game_text', '')
            self.started = msg.data.get('started', False)
            if self.lobby_callback:
                self.lobby_callback(self.players, self.game_text, self.started)

        elif msg.type == MSG_TYPE_COUNTDOWN:
            self.countdown = msg.data.get('seconds', 0)
            if self.countdown_callback:
                self.countdown_callback(self.countdown)

        elif msg.type == MSG_TYPE_START:
            self.game_text = msg.data.get('game_text', '')
            self.started = True
            self.finished = False
            if self.start_callback:
                self.start_callback(self.game_text)

        elif msg.type == MSG_TYPE_PROGRESS:
            self.players = msg.data.get('players', [])
            self.total_chars = msg.data.get('total_chars', 0)
            if self.progress_callback:
                self.progress_callback(self.players, self.total_chars)

        elif msg.type == MSG_TYPE_FINISH:
            self.finished = True
            self.winner_id = msg.data.get('winner_id')
            players_data = msg.data.get('players', [])
            if self.finish_callback:
                self.finish_callback(self.winner_id, players_data)

    def _send(self, msg: Message):
        with self.lock:
            self.send_buffer.append(msg)

    def send_ready(self, ready: bool = True):
        self._send(Message(MSG_TYPE_READY, {'ready': ready}))

    def send_progress(self, pos: int, wpm: float):
        self._send(Message(MSG_TYPE_PROGRESS, {'pos': pos, 'wpm': wpm}))

    def send_finish(self, stats: Dict):
        self._send(Message(MSG_TYPE_FINISH, {'stats': stats}))

    def is_connected(self) -> bool:
        return self.running and self.sock is not None

    def close(self):
        self.running = False
        with self.lock:
            if self.sock:
                try:
                    self.sock.close()
                except OSError:
                    pass
                self.sock = None
