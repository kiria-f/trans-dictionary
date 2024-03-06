import sys
import os
import json
from typing import NewType, Union
from msvcrt import getch

insertion_any_form = NewType('insertion_any_form', Union[
    str,
    tuple[str, int],
    tuple[str, ...],
    list[str],
    tuple[tuple[str, int], ...],
    list[tuple[str, int]]])

insertion = NewType('insertion', list[tuple[str, int]])


class Term:
    clear_code = '\033[1J'
    reset_pos_code = '\033[H'
    hide_cursor_code = '\033[?25l'
    show_cursor_code = '\033[?25h'

    width, height = os.get_terminal_size()
    in_width, in_height = width - 2, height - 2
    buffer = [' ' * width] * height

    @staticmethod
    def clear():
        title = 'Trans Dictionary'
        Term.buffer = ['│' + ' ' * Term.in_width + '│'] * Term.height
        Term.buffer[0] = '╭' + f'┐{title}┌'.center(Term.in_width, '─') + '╮'
        Term.buffer[Term.height - 1] = '╰' + '─' * Term.in_width + '╯'

    @staticmethod
    def draw():
        print(Term.reset_pos_code, Term.hide_cursor_code, '\n'.join(Term.buffer), sep='', end='')

    @staticmethod
    def _prepare_text(
            text: insertion_any_form):
        if isinstance(text, str):
            return ((text, len(text)),)
        if isinstance(text, tuple) and len(text) == 2 and isinstance(text[1], int):
            return (text,)
        if isinstance(text, tuple) or isinstance(text, list):
            text_mod = []
            for line in text:
                if isinstance(line, str):
                    text_mod.append((line, len(line)))
                elif isinstance(line, tuple) and len(line) == 2 and isinstance(line[1], int):
                    text_mod.append(line)
            return text_mod
        return []

    @staticmethod
    def insert(
            text: insertion_any_form,
            y: int | None = None, align_center: bool = False):
        text = Term._prepare_text(text)
        if y is None:
            y = (Term.in_height - len(text)) // 2
        if y < 0:
            y = Term.in_height + y
        for i in range(len(text)):
            line = text[i][0]
            line_width = text[i][1]
            if align_center:
                x = (Term.in_width - line_width) // 2
                line = ' ' * x + line + ' ' * (Term.in_width - x - line_width)
            else:
                line += ' ' * (Term.in_width - line_width)
            Term.buffer[y + i] = '│' + line + '│'


class Color:
    std_colors = ['black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white', 'default']
    code = {
        'full_reset': '\033[0m',
        'fg': dict(zip(std_colors, map(lambda x: f'\033[{x}m', list(range(30, 38)) + [39]))),
        'bg': dict(zip(std_colors, map(lambda x: f'\033[{x}m', list(range(40, 48)) + [49]))),
        'bfg': dict(zip(std_colors, map(lambda x: f'\033[{x}m', list(range(90, 98)) + [99]))),
        'bbg': dict(zip(std_colors, map(lambda x: f'\033[{x}m', list(range(100, 108)) + [109]))),
    }

    @staticmethod
    def hex2sgr(color: str, background: bool = False):
        color = color.lstrip('#')
        r, g, b = int(color[:2], 16), int(color[2:4], 16), int(color[4:], 16)
        return f'\033[{"48" if background else "38"};2;{r};{g};{b}m'


class Border:
    HORIZ = '─'  # '\u2500'
    VERT = '│'  # '\u2502'
    CORNER_BR = '┌'  # '\u250c'
    CORNER_BL = '┐'  # '\u2510'
    CORNER_TR = '└'  # '\u2514'
    CORNER_TL = '┘'  # '\u2518'
    CORNER_VR = '├'  # '\u251c'
    CORNER_VL = '┤'  # '\u2524'
    CORNER_HB = '┬'  # '\u252c'
    CORNER_HT = '┴'  # '\u2534'
    ARC_BR = '╭'  # '\u256d'
    ARC_BL = '╮'  # '\u256e'
    ARC_TL = '╯'  # '\u256f'
    ARC_TR = '╰'  # '\u2570'


class State:
    class Enum:
        MENU = 0
        SCROLL = 1
        ADD = 2
        SEARCH = 3
        QUIT = 4

    class ScrollMode:
        STRAIGHT = 0
        REVERSE = 1

    state = Enum.MENU
    input = ''
    scroll_mode = ScrollMode.STRAIGHT


MENU = [
    '╭─────────────┬─────────────╮',  # 0
    '│  Add Phrase │   Search    │',  # 1
    '│     [A]     │     [S]     │',  # 2
    '├─────────────┴─────────────┤',  # 3
    '│            Run            │',  # 4
    '│          [Enter]          │',  # 5
    '╰───────────────────────────╯'  # 6
]
MENU[2] = MENU[2].replace('[A]', Color.code['fg']['green'] + '[A]' + Color.code['fg']['default'])
MENU[2] = MENU[2].replace('[S]', Color.code['fg']['green'] + '[S]' + Color.code['fg']['default'])
MENU[5] = MENU[5].replace('[Enter]', Color.code['fg']['green'] + '[Enter]' + Color.code['fg']['default'])
MENU = list(map(lambda x: (x, 29), MENU))

with open("db.json", "r") as db_file:
    db = json.load(db_file)

os.system('cls' if os.name == 'nt' else 'clear')
State.state = State.Enum.MENU
c = b"'"
Term.clear()
Term.insert(MENU, align_center=True)
while State.state != State.Enum.QUIT:
    Term.draw()
    c = getch()

    Term.clear()
    if State.state == State.Enum.MENU:
        Term.insert(MENU, align_center=True)
    if State.state == State.Enum.MENU:
        if c == b'a':
            # State.state = State.Enum.ADD
            Term.insert('add', -2)
        elif c == b's':
            # State.state = State.Enum.SEARCH
            Term.insert('search', -2)
        elif c == b'\r':
            # State.state = State.Enum.SCROLL
            Term.insert('scroll', -2)
        if c == b'q':
            State.state = State.Enum.QUIT

os.system('cls' if os.name == 'nt' else 'clear')
