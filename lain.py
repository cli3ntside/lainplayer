import curses
import random
import pygame
import time
import os
import glob
from pathlib import Path

class MusicPlayer:
    def __init__(self):
        self.tracks = []
        for ext in ['*.mp3', '*.wav', '*.ogg', '*.flac']:
            self.tracks.extend(glob.glob(f'bin/{ext}'))
        if not self.tracks:
            raise RuntimeError("There are no tracks bruh😭")
        self.current_track_index = random.randint(0, len(self.tracks) - 1)
        self.is_muted = False 
        self.track_length = 180
        pygame.mixer.init()
        self.load_current_track()

    def load_current_track(self):
        pygame.mixer.music.load(self.tracks[self.current_track_index])
        pygame.mixer.music.play()
        
    def skip(self):
        self.current_track_index = (self.current_track_index + 1) % len(self.tracks)
        self.load_current_track()

    def rewind(self):
        self.current_track_index = (self.current_track_index - 1) % len(self.tracks)
        self.load_current_track()

    def get_current_track_name(self):
        return Path(self.tracks[self.current_track_index]).stem

    def get_progress(self):
        if not pygame.mixer.music.get_busy():
            return 0
        current_time = pygame.mixer.music.get_pos() / 1000
        return current_time
    
    def get_track_length(self):
        return self.track_length

ascii_art = [
    "          _..--¯¯¯¯--.._",
    "      ,-''              `-.",
    "    ,'                     `.",
    "   ,                         \\",
    "  /                           \\",
    " /          ′.                 \\",
    "'          /  ││                ;",
    ";       n /│  │/         │      │",
    "│      / v    /\\/`-'v√\\'.│\\     ,",
    ":    /v`,———         ————.^.    ;",
    "'   │  /′@@`,        ,@@ `\\│    ;",
    "│  n│  '.@@/         \\@@  /│\\  │;",
    "` │ `    ¯¯¯          ¯¯¯  │ \\/││",
    " \\ \\ \\                     │ /\\/",
    " '; `-\\          `′       /│/ │′",
    "  `    \\       —          /│  │",
    "   `    `.              .' │  │",
    "    v,_   `;._     _.-;    │  /",
    "       `'`\\│-_`'-''__/^'^' │ │",
    "              ¯¯¯¯¯        │ │",
    "                           │ /",
    "                           ││",
    "                           │,"
]

protected_positions = {
    9: list(range(6, 24)),
    10: list(range(4, 25)),
    11: list(range(4, 26)),
    12: list(range(3, 26)),
    13: list(range(3, 24)),
    14: list(range(3, 24)),
    15: list(range(3, 24)),
    16: list(range(3, 27)),
    17: list(range(3, 26)),
    18: list(range(3, 28)),
    19: list(range(3, 27)),
}

protected_positions[10] = list(set(protected_positions[10]))
protected_positions[11] = list(set(protected_positions[11]))
protected_positions[12] = list(set(protected_positions[12]))
protected_positions[16] = list(set(protected_positions[16]))

def create_player_ui(track_name, is_muted, progress, player):
    minutes = int(progress // 60)
    seconds = int(progress % 60)
    progress_bar_width = 30
    
    total_seconds = player.get_track_length()
    filled = int((progress / total_seconds) * progress_bar_width)
    
    ui = [
        f" {'⏸' if is_muted else '▶'} {track_name:<25} {minutes:02d}:{seconds:02d}",
        f" [{('=' * filled) + '>' + (' ' * (progress_bar_width - filled - 1))}]"
    ]
    return ui

def replace_surrounded_spaces(ascii_art):
    result = []
    for line_number, line in enumerate(ascii_art):
        new_line = []
        i = 0

        while i < len(line):
            if line[i] == ' ':
                start = i
                while i < len(line) and line[i] == ' ':
                    i += 1
                end = i
                if start > 0 and end < len(line) and line[start-1] != ' ' and line[end] != ' ':
                    if line_number not in protected_positions or not any(pos in range(start, end) for pos in protected_positions[line_number]):
                        new_line.append('#' * (end - start))
                    else:
                        new_line.append(line[start:end])
                else:
                    new_line.append(line[start:end])
            else:
                new_line.append(line[i])
                i += 1

        new_line = ''.join(new_line)
        result.append(new_line)
    return result

def reveal_ascii_art(stdscr, ascii_art):
    curses.curs_set(0)
    stdscr.nodelay(1)
    stdscr.timeout(100)

    start_time = time.time()
    total_lines = len(ascii_art)
    while time.time() - start_time < 2:
        elapsed = time.time() - start_time
        lines_to_show = int((elapsed / 2) * total_lines)
        stdscr.clear()
        for i in range(lines_to_show):
            x_position = (stdscr.getmaxyx()[1] - len(ascii_art[i])) // 2
            stdscr.addstr(i + 4, x_position, ascii_art[i])
        stdscr.refresh()
        time.sleep(0.1)

def animate_symbols(stdscr, ascii_art):
    player = MusicPlayer()
    reveal_ascii_art(stdscr, ascii_art)

    curses.curs_set(0)
    stdscr.nodelay(1)
    stdscr.timeout(100)

    while True:
        stdscr.clear()
        
        player_ui = create_player_ui(
            player.get_current_track_name(),
            player.is_muted,
            player.get_progress(),
            player
        )
        
        for i, line in enumerate(player_ui):
            stdscr.addstr(i, 0, line)

        for line_number, line in enumerate(ascii_art):
            animated_line = ''.join(
                random.choice(['#', '@', '?', '!']) if char == '#' else char for char in line
            )
            x_position = (stdscr.getmaxyx()[1] - len(animated_line)) // 2
            stdscr.addstr(line_number + 4, x_position, animated_line)
        
        status = "Commands: [m]ute | [u]nmute | [s]kip | [r]ewind | [q]uit"
        x_position = (stdscr.getmaxyx()[1] - len(status)) // 2
        stdscr.addstr(len(ascii_art) + 5, x_position, status)
        stdscr.refresh()

        try:
            key = stdscr.getch()
            if key == ord('m') and not player.is_muted:
                pygame.mixer.music.set_volume(0.0)
                player.is_muted = True
            elif key == ord('u') and player.is_muted:
                pygame.mixer.music.set_volume(0.5)
                player.is_muted = False
            elif key == ord('s'):
                player.skip()
            elif key == ord('r'):
                player.rewind()
            elif key == ord('q'):
                break
        except curses.error:
            continue

        if not pygame.mixer.music.get_busy():
            player.skip()

    pygame.mixer.music.stop()

def main():
    os.system('cls' if os.name == 'nt' else 'clear')

    updated_art = replace_surrounded_spaces(ascii_art)
    curses.wrapper(animate_symbols, updated_art)

if __name__ == "__main__":
    main()