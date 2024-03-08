import os
import json
from dataclasses import dataclass
import random
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
    '~': 'Ё',
    'Q': 'Й',
    'W': 'Ц',
    'E': 'У',
    'R': 'К',
    'T': 'Е',
    'Y': 'Н',
    'U': 'Г',
    'I': 'Ш',
    'O': 'Щ',
    'P': 'З',
    '{': 'Х',
    '}': 'Ъ',
    'A': 'Ф',
    'S': 'Ы',
    'D': 'В',
    'F': 'А',
    'G': 'П',
    'H': 'Р',
    'J': 'О',
    'K': 'Л',
    'L': 'Д',
    ':': 'Ж',
    '"': 'Э',
    'Z': 'Я',
    'X': 'Ч',
    'C': 'С',
    'V': 'М',
    'B': 'И',
    'N': 'Т',
    'M': 'Ь',
    '<': 'Б',
    '>': 'Ю'
}

ru2en = {v: k for k, v in en2ru.items()}


def visible_len(line: str) -> int:
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


class Key:
    class Special:
        PRINTABLE = 0
        ENTER = 1
        BACKSPACE = 2
        TAB = 3
        ESC = 4
        SHIFT = 5
        CTRL = 6
        ARROW_UP = 10
        ARROW_DOWN = 11
        ARROW_LEFT = 12
        ARROW_RIGHT = 13

    printable: str
    special: int
    special_prints: dict[int, str] = {
        Special.PRINTABLE: '⌨',
        Special.ENTER: '↵',
        Special.BACKSPACE: '⌫',
        Special.TAB: '↹',
        Special.ESC: '⎋',
        Special.SHIFT: '⇧',
        Special.CTRL: '⌃',
        Special.ARROW_UP: '↑',
        Special.ARROW_DOWN: '↓',
        Special.ARROW_LEFT: '←',
        Special.ARROW_RIGHT: '→',
    }

    def __init__(self, value: str | int) -> None:
        if isinstance(value, str):
            self.printable = value
            self.special = Key.Special.PRINTABLE
        else:
            self.special = value
            self.printable = ''

    def __eq__(self, other) -> bool:
        if isinstance(other, str):
            return self.printable == other
        if isinstance(other, int):
            return self.special == other
        return self == other

    def __hash__(self):
        return hash(self.printable)

    def __str__(self) -> str:
        return self.printable

    def force_str(self) -> str:
        if self.special:
            return self.special_prints[self.special]
        return self.printable


def getch_nt() -> Key:
    b = getch()
    if b == b'\r':
        return Key(Key.Special.ENTER)
    if b == b'\x08':
        return Key(Key.Special.BACKSPACE)
    if b == b'\\':
        return Key('\\')
    if b == b'\t':
        return Key(Key.Special.TAB)
    if b == b'\xe0':
        b = getch()
        if b == b'H':
            return Key(Key.Special.ARROW_UP)
        if b == b'P':
            return Key(Key.Special.ARROW_DOWN)
        if b == b'K':
            return Key(Key.Special.ARROW_LEFT)
        if b == b'M':
            return Key(Key.Special.ARROW_RIGHT)
    return Key(str(b)[2:-1])


def getch_unix() -> Key:
    b = os.read(0, 1)
    return Key(str(b)[2:-1])


@dataclass
class Record:
    translation: str
    rate: float

    def __init__(self, translation: str, rate: float = 1) -> None:
        self.translation = translation
        self.rate = rate


class RecordEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Record):
            return obj.__dict__
        return json.JSONEncoder.default(self, obj)


class DB:
    db: dict[str, Record] = {}

    @staticmethod
    def load() -> None:
        with open('db.json', 'r', encoding='utf-8') as db_file:
            db_raw = json.load(db_file)
        DB.db = {k: Record(v['translation'], v['rate']) for k, v in db_raw.items()}

    @staticmethod
    def dump() -> None:
        with open('db.json', 'w', encoding='utf-8') as db_file:
            json.dump(DB.db, db_file, cls=RecordEncoder, ensure_ascii=False, indent=4)


class Term:
    clear_code = '\033[1J'
    reset_pos_code = '\033[H'
    hide_cursor_code = '\033[?25l'
    show_cursor_code = '\033[?25h'

    width, height = os.get_terminal_size()
    in_width, in_height = width - 2, height - 2
    buffer = [' ' * width] * height

    @staticmethod
    def refresh() -> None:
        os.system('cls' if os.name == 'nt' else 'clear')
        Term.width, Term.height = os.get_terminal_size()
        Term.in_width, Term.in_height = Term.width - 2, Term.height - 2

    @staticmethod
    def reset() -> None:
        title = 'Trans Dictionary'
        Term.buffer = ['│' + ' ' * Term.in_width + '│'] * Term.height
        Term.buffer[0] = '╭' + f'┐{title}┌'.center(Term.in_width, '─') + '╮'
        Term.buffer[Term.height - 1] = '╰' + '─' * Term.in_width + '╯'

    @staticmethod
    def draw() -> None:
        if DEBUG:
            print(Term.hide_cursor_code, '\n'.join(Term.buffer), sep='', end='')
        else:
            print(Term.reset_pos_code, Term.hide_cursor_code, '\n'.join(Term.buffer), sep='', end='')

    @staticmethod
    def _prepare_text(text: insertion_any_form) -> list[tuple[str, int]]:
        if isinstance(text, str):
            return [(text, visible_len(text))]
        if isinstance(text, tuple) and len(text) == 2 and isinstance(text[1], int):
            return [(text[0], text[1])]
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
    def insert(text: insertion_any_form, y: int | None = None, align_center: bool = False) -> None:
        text = Term._prepare_text(text)
        if y is None:
            y = (Term.in_height - len(text)) // 2 + 1
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
    def from_hex(color: str, background: bool = False) -> str:
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
        EXPLORE = 'explore'
        QUIT = 'quit'

    class Direction:
        STRAIGHT = 0
        REVERSE = 1

    state = Enum.MENU
    parameter = None
    input = ''
    scroll_mode = Direction.STRAIGHT
    explore_mode = Direction.STRAIGHT
    scroll_reveal = False
    first_time = False


MENU = [
    '╭──────────────┬──────────────╮',  # 0
    '│ [A]dd Phrase │  [E]xplore   │',  # 1
    '├──────────────┴──────────────┤',  # 2
    '│             Run             │',  # 3
    '│           [Enter]           │',  # 4
    '├──────────────┬──────────────┤',  # 5
    '│  [S]ettings  │  [R]efresh   │',  # 6
    '╰──────┬───────┴───────┬──────╯',  # 7
    '       │   🠜 [Q]uit    │       ',  # 8
    '       ╰───────────────╯       ',  # 9
]
MENU[1] = MENU[1].replace('[A]', Style.GREEN + '[A]' + Style.DEFAULT)
MENU[1] = MENU[1].replace('[E]', Style.GREEN + '[E]' + Style.DEFAULT)
MENU[4] = MENU[4].replace('[Enter]', Style.GREEN + '[Enter]' + Style.DEFAULT)
MENU[6] = MENU[6].replace('[S]', Style.GREEN + '[S]' + Style.DEFAULT)
MENU[6] = MENU[6].replace('[R]', Style.GREEN + '[R]' + Style.DEFAULT)
MENU[8] = MENU[8].replace('[Q]', Style.RED + '[Q]' + Style.DEFAULT)


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


def menu_handle(k: Key):
    if State.state == State.Enum.MENU:
        if k == 'a':
            State.parameter = ''
            State.state = State.Enum.ADD
        elif k == 'e':
            State.parameter = ''
            State.state = State.Enum.EXPLORE
        elif k == Key.Special.ENTER:
            State.parameter = ''
            State.first_time = True
            State.state = State.Enum.SCROLL
        elif k == 'r':
            Term.refresh()
        elif k == 'q':
            State.state = State.Enum.QUIT
        else:
            message = (Style.RED + 'Unknown: ' +
                       Style.BRIGHT_BLACK + '[' +
                       Style.DEFAULT + k.force_str() +
                       Style.BRIGHT_BLACK + ']' +
                       Style.DEFAULT)
            State.parameter = message


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
        if len(State.parameter) - dash_index - 3 < 7:
            tip += '…'
    else:
        tip += '…'
    tip = '    ' + Style.BRIGHT_BLUE + tip + Style.DEFAULT
    Term.insert(tip, y=-2)

    if State.parameter != '':
        token = State.parameter.lower()
        if ' - ' in token:
            token = token[:token.index(' - ')]
        filtered = sorted(filter(lambda s: token in s.lower(), DB.db.keys()), reverse=True)[:9]
        for i in range(len(filtered)):
            Term.insert(f'{Style.BRIGHT_BLACK}  >{Style.DEFAULT} ' + filtered[i], -5 - i)


def add_handle(k: Key):
    if k == '/':
        State.state = State.Enum.MENU
        State.parameter = None
    elif k == Key.Special.ENTER:
        if ' - ' in State.parameter:
            key, val = State.parameter.split(' - ', 1)
            val = Record(val)
            DB.db[key] = val
            DB.dump()
            phrase = Style.BRIGHT_BLUE + State.parameter[:State.parameter.index(" - ")] + Style.DEFAULT
            State.parameter = f'Phrase {phrase} is successfully added'
        else:
            State.parameter = Style.RED + 'Phrase is not added' + Style.DEFAULT
        State.state = State.Enum.MENU
    elif k == Key.Special.BACKSPACE:
        if State.parameter:
            State.parameter = State.parameter[:-1]
        if State.parameter == 'to ':
            State.parameter = 'To '
    else:
        if ' - ' in State.parameter:
            if State.parameter[-1] == '░':
                State.parameter = State.parameter[:-1]
                if k in (',', '.', ';'):
                    State.parameter += str(k)
            elif k in en2ru:
                if State.parameter.index(' - ') == len(State.parameter) - 3:
                    State.parameter += en2ru[k].upper()
                else:
                    State.parameter += en2ru[k]
            else:
                if k == '\\' and State.parameter.index(' - ') != len(State.parameter) - 3:
                    State.parameter += '░'
                else:
                    State.parameter += str(k)
        else:
            if len(State.parameter) == 0:
                State.parameter += str(k).upper()
            elif State.parameter == 'To ':
                State.parameter = 'to ' + str(k).upper()
            else:
                State.parameter += str(k)


def explore_print():
    Term.insert(Style.BLINK_ON + '  ⮞ ' + Style.BLINK_OFF + State.parameter, y=-3)
    if State.scroll_mode == State.Direction.STRAIGHT:
        tip = Style.BRIGHT_BLUE + 'Search'
    else:
        tip = Style.GREEN + 'Поиск'
    Term.insert('    ' + tip + Style.BRIGHT_BLACK + '  [Tab] to swap' + Style.DEFAULT, y=-2)

    if State.parameter != '':
        filtered = sorted(filter(lambda s: State.parameter in s.lower(), DB.db.keys()), reverse=True)[:9]
        for i in range(len(filtered)):
            Term.insert(f'{Style.BRIGHT_BLACK}[{i + 1}]{Style.DEFAULT} ' + filtered[i], -5 - i)


def explore_handle(k: Key):
    if k == '/':
        State.state = State.Enum.MENU
        State.parameter = None
    elif k == Key.Special.TAB:
        State.scroll_mode = 1 - State.scroll_mode
        State.parameter = ''
    elif k == '\b':
        if State.parameter:
            State.parameter = State.parameter[:-1]
    else:
        if State.scroll_mode == State.Direction.REVERSE and k in en2ru:
            State.parameter += en2ru[k]
        else:
            State.parameter += k


def scroll_print():
    if State.scroll_reveal:
        phrase = State.parameter
    else:
        items = DB.db.items()
        rate_sum = 0
        for item in items:
            rate_sum += item[1].rate
        rnd = random.random() * rate_sum
        phrase: None | tuple[str, Record] = None
        for item in items:
            if rnd < item[1].rate:
                phrase = item
                break
            rnd -= item[1].rate
    Term.insert(phrase[0], Term.in_height // 2, True)
    if State.first_time:
        Term.insert(
            f'{Style.GREEN}[/]{Style.DEFAULT} Menu, '
            f'{Style.GREEN}[\']{Style.DEFAULT} Reveal, '
            f'{Style.GREEN}[Enter]{Style.DEFAULT} Scroll next',
            Term.in_height // 2 + 2,
            True)
    if State.scroll_reveal:
        Term.insert(Style.YELLOW + phrase[1].translation + Style.DEFAULT, Term.in_height // 2 + 2, True)
    State.parameter = phrase


def scroll_handle(k: Key):
    if k == '/':
        State.state = State.Enum.MENU
        State.parameter = None
    elif k == '\n':
        if not State.scroll_reveal:
            State.parameter[1].rate *= 0.75
        DB.dump()
        State.scroll_reveal = False
    elif k == "'":
        State.parameter[1].rate *= 1.25
        DB.dump()
        State.scroll_reveal = True


def main():
    DB.load()
    if not DEBUG:
        os.system('cls' if os.name == 'nt' else 'clear')
    logic = {
        State.Enum.MENU: LogicBlock(menu_print, menu_handle),
        State.Enum.ADD: LogicBlock(add_print, add_handle),
        State.Enum.EXPLORE: LogicBlock(explore_print, explore_handle),
        State.Enum.SCROLL: LogicBlock(scroll_print, scroll_handle)
    }

    State.state = State.Enum.MENU
    State.next_call = lambda: menu_print()
    Term.reset()
    while State.state != State.Enum.QUIT:
        logic[State.state].printer()
        Term.draw()
        if os.name == 'nt':
            c = getch_nt()
        else:
            c = getch_unix()
        State.first_time = State.state == State.Enum.MENU
        logic[State.state].handler(c)
        Term.reset()

    print(Style.RESET, end='')
    if not DEBUG:
        os.system('cls' if os.name == 'nt' else 'clear')


if __name__ == '__main__':
    main()
