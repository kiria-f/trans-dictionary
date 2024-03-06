import os
import json
from typing import NewType, Union
from msvcrt import getch

DEBUG = False

insertion_any_form = NewType('insertion_any_form', Union[
    str,
    tuple[str, int],
    tuple[str, ...],
    list[str],
    tuple[tuple[str, int], ...],
    list[tuple[str, int]]])

insertion = NewType('insertion', list[tuple[str, int]])

en2ru = {
    '`': 'ё',
    'q': 'й',
    'w': 'ц',
    'e': 'у',
    'r': 'к',
    't': 'е',
    'y': 'н',
    'u': 'г',
    'i': 'ш',
    'o': 'щ',
    'p': 'з',
    '[': 'х',
    ']': 'ъ',
    'a': 'ф',
    's': 'ы',
    'd': 'в',
    'f': 'а',
    'g': 'п',
    'h': 'р',
    'j': 'о',
    'k': 'л',
    'l': 'д',
    ';': 'ж',
    "'": 'э',
    'z': 'я',
    'x': 'ч',
    'c': 'с',
    'v': 'м',
    'b': 'и',
    'n': 'т',
    'm': 'ь',
    ',': 'б',
    '.': 'ю',
}


def visible_len(line: str):
    vl = 0
    i = 0
    while i < len(line):
        if line[i] == '\033':
            while line[i] != 'm':
                i += 1
        else:
            vl += 1
        i += 1
    return vl


class Term:
    clear_code = '\033[1J'
    reset_pos_code = '\033[H'
    hide_cursor_code = '\033[?25l'
    show_cursor_code = '\033[?25h'

    width, height = os.get_terminal_size()
    in_width, in_height = width - 2, height - 2
    buffer = [' ' * width] * height

    @staticmethod
    def reset():
        title = 'Trans Dictionary'
        Term.buffer = ['│' + ' ' * Term.in_width + '│'] * Term.height
        Term.buffer[0] = '╭' + f'┐{title}┌'.center(Term.in_width, '─') + '╮'
        Term.buffer[Term.height - 1] = '╰' + '─' * Term.in_width + '╯'

    @staticmethod
    def draw():
        if DEBUG:
            print(Term.hide_cursor_code, '\n'.join(Term.buffer), sep='', end='')
        else:
            print(Term.reset_pos_code, Term.hide_cursor_code, '\n'.join(Term.buffer), sep='', end='')

    @staticmethod
    def _prepare_text(text: insertion_any_form):
        if isinstance(text, str):
            return [(text, visible_len(text))]
        if isinstance(text, tuple) and len(text) == 2 and isinstance(text[1], int):
            return [text]
        if isinstance(text, tuple) or isinstance(text, list):
            text_mod = []
            for line in text:
                if isinstance(line, str):
                    text_mod.append((line, visible_len(line)))
                elif isinstance(line, tuple) and len(line) == 2 and isinstance(line[1], int):
                    text_mod.append(line)
            return text_mod
        return []

    @staticmethod
    def insert(text: insertion_any_form, y: int | None = None, align_center: bool = False):
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


class Style:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    BLINK_ON = '\033[5m'
    BLINK_OFF = '\033[25m'
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    DEFAULT = '\033[39m'
    BLACK_BG = '\033[40m'
    RED_BG = '\033[41m'
    GREEN_BG = '\033[42m'
    YELLOW_BG = '\033[43m'
    BLUE_BG = '\033[44m'
    MAGENTA_BG = '\033[45m'
    CYAN_BG = '\033[46m'
    WHITE_BG = '\033[47m'
    DEFAULT_BG = '\033[49m'
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    BRIGHT_BLACK_BG = '\033[100m'
    BRIGHT_RED_BG = '\033[101m'
    BRIGHT_GREEN_BG = '\033[102m'
    BRIGHT_YELLOW_BG = '\033[103m'
    BRIGHT_BLUE_BG = '\033[104m'
    BRIGHT_MAGENTA_BG = '\033[105m'
    BRIGHT_CYAN_BG = '\033[106m'
    BRIGHT_WHITE_BG = '\033[107m'

    @staticmethod
    def from_hex(color: str, background: bool = False):
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
        MENU = 'menu'
        SCROLL = 'scroll'
        ADD = 'add'
        SEARCH = 'search'
        QUIT = 'quit'

    class ScrollMode:
        STRAIGHT = 0
        REVERSE = 1

    state = Enum.MENU
    parameter: None | str = None
    input = ''
    scroll_mode = ScrollMode.STRAIGHT
    db: dict[str, str] = {}


MENU = [
    '╭─────────────┬─────────────╮',  # 0
    '│  Add Phrase │   Search    │',  # 1
    '│     [A]     │     [S]     │',  # 2
    '├─────────────┴─────────────┤',  # 3
    '│            Run            │',  # 4
    '│          [Enter]          │',  # 5
    '╰───────────────────────────╯'  # 6
]
MENU[2] = MENU[2].replace('[A]', Style.GREEN + '[A]' + Style.DEFAULT)
MENU[2] = MENU[2].replace('[S]', Style.GREEN + '[S]' + Style.DEFAULT)
MENU[5] = MENU[5].replace('[Enter]', Style.GREEN + '[Enter]' + Style.DEFAULT)


class LogicBlock:
    printer: callable
    handler: callable

    def __init__(self, printer, handler):
        self.printer = printer
        self.handler = handler


def menu_print():
    Term.insert(MENU, align_center=True)
    if State.parameter is not None:
        Term.insert(State.parameter, -2, True)


def menu_handle(c: bytes):
    if State.state == State.Enum.MENU:
        if c == b'a':
            State.state = State.Enum.ADD
            State.parameter = ''
        elif c == b's':
            State.state = State.Enum.SEARCH
        elif c == b'\r':
            State.state = State.Enum.SCROLL
        elif c == b'q':
            State.state = State.Enum.QUIT
        else:
            token = str(c)[2:-1]
            message = (Style.RED + 'Unknown: ' +
                       Style.BRIGHT_BLACK + '[' +
                       Style.DEFAULT + token +
                       Style.BRIGHT_BLACK + ']' +
                       Style.DEFAULT)
            State.parameter = (message, 11 + len(token))


def add_print():
    Term.insert(Style.BLINK_ON + '  ⮞ ' + Style.BLINK_OFF + State.parameter, y=-3)
    tip = 'Phrase'[:len(State.parameter)]
    if ' - ' in State.parameter:
        dash_index = State.parameter.index(' - ')
        if dash_index < 6:
            tip = tip[:dash_index] + '…  '
        else:
            tip += ' ' * (dash_index - 3)
        tip += Style.GREEN + 'Перевод'[:len(State.parameter) - dash_index - 3]
    tip = '    ' + Style.BRIGHT_BLUE + tip + Style.DEFAULT
    Term.insert(tip, y=-2)


def add_handle(c: bytes):
    if c == b'/':
        State.state = State.Enum.MENU
        State.parameter = None
    elif c == b'\r':
        if ' - ' in State.parameter:
            key, val = State.parameter.split(' - ', 1)
            State.db[key] = val
            with open('db.json', 'w') as db_file:
                json.dump(State.db, db_file)
        State.state = State.Enum.MENU
        State.parameter = None
    elif c == b'\b':
        if State.parameter:
            State.parameter = State.parameter[:-1]
    else:
        cs = str(c)[2:-1].lower()
        if ' - ' in State.parameter and cs in en2ru:
            if State.parameter.index(' - ') == len(State.parameter) - 3:
                State.parameter += en2ru[cs].upper()
            else:
                State.parameter += en2ru[cs]
        else:
            if len(State.parameter) == 0:
                cs = cs.upper()
            State.parameter += cs


def main():
    with open('db.json', 'r') as db_file:
        State.db = json.load(db_file)
    if not DEBUG:
        os.system('cls' if os.name == 'nt' else 'clear')
    logic = {
        State.Enum.MENU: LogicBlock(menu_print, menu_handle),
        State.Enum.ADD: LogicBlock(add_print, add_handle),
    }

    State.state = State.Enum.MENU
    State.next_call = lambda: menu_print()
    Term.reset()
    while State.state != State.Enum.QUIT:
        logic[State.state].printer()
        Term.draw()
        logic[State.state].handler(getch())
        Term.reset()

    print(Style.RESET, end='')
    if not DEBUG:
        os.system('cls' if os.name == 'nt' else 'clear')


if __name__ == '__main__':
    main()
