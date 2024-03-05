import sys
import os
import json
from msvcrt import getch


class KeyCodes:
    ENTER = 10
    BACKSPACE = 8
    CTRL_BACKSPACE = 127


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
    def insert(text: tuple[tuple[str, int]] | list[tuple[str, int]], y: int = -1, align_center: bool = False):
        if y == -1:
            y = (Term.in_height - len(text)) // 2
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


MENU = [
    '╭─────────────┬─────────────╮',  # 0
    '│  Add Phrase │   Search    │',  # 1
    '│     [A]     │     [S]     │',  # 2
    '├─────────────┴─────────────┤',  # 3
    '│            Run            │',  # 4
    '│          [Enter]          │',  # 5
    '╰───────────────────────────╯'   # 6
]
MENU[2] = MENU[2].replace('[A]', Color.code['fg']['green'] + '[A]' + Color.code['fg']['default'])
MENU[2] = MENU[2].replace('[S]', Color.code['fg']['green'] + '[S]' + Color.code['fg']['default'])
MENU[5] = MENU[5].replace('[Enter]', Color.code['fg']['green'] + '[Enter]' + Color.code['fg']['default'])
MENU = list(map(lambda x: (x, 29), MENU))

with open("db.json", "r") as db_file:
    db = json.load(db_file)

Term.clear()
Term.insert(MENU, align_center=True)
Term.draw()
getch()
os.system('cls' if os.name == 'nt' else 'clear')
