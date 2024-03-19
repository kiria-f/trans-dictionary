import sys
import os
import json
from dataclasses import dataclass
import random
from typing import NewType, Union, Any
import msvcrt
import traceback

DEBUG = False

insertion_any_form = NewType('insertion_any_form', Union[
    str,
    tuple[str, int],
    tuple[str, ...],
    list[str],
    tuple[tuple[str, int], ...],
    list[tuple[str, int]]])

insertion = NewType('insertion', list[tuple[str, int]])

en_keyboard = '`qwertyuiop[]asdfghjkl;\'zxcvbnm,./~QWERTYUIOP{}ASDFGHJKL:"ZXCVBNM<>?'
ru_keyboard = 'ёйцукенгшщзхъфывапролджэячсмитьбю.ЁЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ,'
en2ru = {e: r for e, r in zip(en_keyboard, ru_keyboard)}
ru2en = {r: e for e, r in zip(en_keyboard, ru_keyboard)}


class StrTool:
    @staticmethod
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

    @staticmethod
    def visible_index(line: str, index: int) -> int:
        vi = 0
        i = 0
        while i < index:
            if line[vi] == '\033':
                while line[vi] != 'm':
                    vi += 1
            else:
                i += 1
            vi += 1
        return vi - 1

    @staticmethod
    def format(
            line: str,
            final: bool = False,
            colorize: bool = False,
            palette: dict[str, str] | None = None) -> str:
        if palette is None:
            palette = {
                'phrase': Style.BRIGHT_BLUE,
                'delim': Style.DEFAULT,
                'translation': Style.GREEN
            }
        line = line.lower()
        deline = line.split()
        if len(deline) > 0:
            if deline[0] == 'to' and len(deline) > 1:
                deline[1] = deline[1].capitalize()
            else:
                deline[0] = deline[0].capitalize()
            if colorize:
                deline[0] = palette['phrase'] + deline[0]
        delim = '-'
        if delim in deline:
            delim_index = deline.index(delim)
            while deline.count(delim) > 1:
                next_index = deline.index(delim, delim_index + 1)
                deline.pop(next_index)
            if colorize:
                deline[delim_index] = palette['delim'] + delim
            tr_index = delim_index + 1
            if tr_index < len(deline):
                deline[tr_index] = deline[tr_index].capitalize()
                if colorize:
                    deline[tr_index] = palette['translation'] + deline[tr_index]
        return ' '.join(deline)


class Key:
    class Special:
        PRINTABLE = 0
        ENTER = 1
        BACKSPACE = 2
        TAB = 3
        ESC = 4
        SHIFT = 5
        CTRL = 6
        HOME = 7
        END = 8
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
        Special.HOME: '↖',
        Special.END: '↘',
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
    data: dict[str, Record] = {}

    @staticmethod
    def load() -> None:
        with open('db.json', 'r', encoding='utf-8') as db_file:
            db_raw = json.load(db_file)
        DB.data = {k: Record(v['translation'], v['rate']) for k, v in db_raw.items()}

    @staticmethod
    def dump() -> None:
        with open('db.json', 'w', encoding='utf-8') as db_file:
            json.dump(DB.data, db_file, cls=RecordEncoder, ensure_ascii=False, indent=4)


class Term:
    clear_code = '\033[1J'
    reset_pos_code = '\033[H'
    save_pos_code = '\033s'
    restore_pos_code = '\033u'
    hide_cursor_code = '\033[?25l'
    show_cursor_code = '\033[?25h'

    width, height = os.get_terminal_size()
    in_width, in_height = width - 2, height - 2
    buffer = [' ' * width] * height
    cursor: tuple[int, int] | None = None

    @staticmethod
    def clear():
        os.system('cls' if os.name == 'nt' else 'clear')

    @staticmethod
    def refresh() -> None:
        Term.clear()
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
        print('' if DEBUG else Term.reset_pos_code,
              '\n'.join(Term.buffer),
              Term.hide_cursor_code if Term.cursor is None else (
                      Term.show_cursor_code +
                      f'\033[{Term.cursor[0]};{Term.cursor[1]}H'),
              sep='', end='', flush=True)
        Term.cursor = None

    @staticmethod
    def set_cursor(y: int, x: int) -> None:
        if y < 0:
            y = Term.in_height + y
        if x < 0:
            x = Term.in_width + x
        Term.cursor = (y + 1, x + 1)

    @staticmethod
    def _prepare_text(text: insertion_any_form) -> list[tuple[str, int]]:
        if isinstance(text, str):
            return [(text, StrTool.visible_len(text))]
        if isinstance(text, tuple) and len(text) == 2 and isinstance(text[1], int):
            return [(text[0], text[1])]
        if isinstance(text, tuple) or isinstance(text, list):
            text_mod = []
            for line in text:
                if isinstance(line, str):
                    text_mod.append((line, StrTool.visible_len(line)))
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
        y += 1
        for i in range(len(text)):
            line = text[i][0]
            line_width = text[i][1]
            if align_center:
                x = (Term.in_width - line_width) // 2
                line = ' ' * x + line + ' ' * (Term.in_width - x - line_width)
            else:
                line += ' ' * (Term.in_width - line_width)
            v_len = StrTool.visible_len(line)
            if v_len > Term.in_width:
                line = line[:StrTool.visible_index(line, Term.in_width)] + '…'
            Term.buffer[y + i] = '│' + line + '│'

    @staticmethod
    def getch() -> Key:
        if os.name == 'nt':
            b = msvcrt.getch()
            if b == b'\r':
                return Key(Key.Special.ENTER)
            if b == b'\x08':
                return Key(Key.Special.BACKSPACE)
            if b == b'\\':
                return Key('\\')
            if b == b'\t':
                return Key(Key.Special.TAB)
            if b == b'\x1b':
                return Key(Key.Special.ESC)
            if b == b'\xe0':
                b = msvcrt.getch()
                if b == b'H':
                    return Key(Key.Special.ARROW_UP)
                if b == b'P':
                    return Key(Key.Special.ARROW_DOWN)
                if b == b'K':
                    return Key(Key.Special.ARROW_LEFT)
                if b == b'M':
                    return Key(Key.Special.ARROW_RIGHT)
            if b == b'\x00':
                b = msvcrt.getch()
                if b == b'G':
                    return Key(Key.Special.HOME)
                if b == b'O':
                    return Key(Key.Special.END)
            return Key(str(b)[2:-1])
        else:
            b = os.read(0, 1)
            return Key(str(b)[2:-1])


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
        if len(color) == 3:
            color = ''.join([c * 2 for c in color])
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
        EDIT = 'edit'

    class Direction:
        STRAIGHT = 0
        REVERSE = 1

    state = Enum.MENU
    parameter: Any = {}
    input = ''
    scroll_mode = Direction.STRAIGHT
    explore_mode = Direction.STRAIGHT
    cursor_index = -1


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
    if State.parameter is None:
        Term.insert(f'{Style.GREEN}[/]{Style.DEFAULT} Back to menu from anywhere', -2, True)
    elif State.parameter:
        Term.insert(State.parameter, -2, True)


def menu_handle(k: Key):
    state_change = True
    if k == 'a':
        State.state = State.Enum.ADD
    elif k == 'e':
        State.state = State.Enum.EXPLORE
    elif k == Key.Special.ENTER:
        State.first_time = True
        State.state = State.Enum.SCROLL
    elif k == 'r':
        Term.refresh()
        state_change = False
    elif k == 'q':
        State.state = State.Enum.QUIT
    else:
        State.parameter = (Style.RED + 'Unknown: ' +
                           Style.BRIGHT_BLACK + '[' +
                           Style.DEFAULT + k.force_str() + (' ' if k in (k.Special.BACKSPACE,) else '') +
                           Style.BRIGHT_BLACK + ']' +
                           Style.DEFAULT)
        state_change = False

    if state_change:
        State.parameter = None


def add_print():
    if State.parameter is None:
        State.parameter = ''

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
        filtered = sorted(filter(lambda item: token in item[0].lower(), DB.data.items()), reverse=True)[:9]
        for i in range(len(filtered)):
            Term.insert(f'{Style.BRIGHT_BLACK}  >{Style.DEFAULT} '
                        + filtered[i][0] + ' - ' + filtered[i][1].translation, -5 - i)
    Term.set_cursor(-2, len(State.parameter) + 5)


def add_handle(k: Key):
    if k == '/':
        State.state = State.Enum.MENU
        State.parameter = None
    elif k == Key.Special.ENTER:
        if ' - ' in State.parameter:
            key, val = State.parameter.split(' - ', 1)
            val = Record(val)
            DB.data[key] = val
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
    first_time = State.parameter is None
    if first_time:
        State.parameter = {
            'promt': '',
            'filtered': [],
            'selection': -1
        }

    Term.insert(Style.BLINK_ON + '  ⮞ ' + Style.BLINK_OFF + State.parameter['promt'], y=-3)
    if State.scroll_mode == State.Direction.STRAIGHT:
        tip = Style.BRIGHT_BLUE + 'Search'
    else:
        tip = Style.GREEN + 'Поиск'
    Term.insert('    ' + tip + Style.BRIGHT_BLACK + '  [Tab] to swap' + Style.DEFAULT, y=-2)

    for i in range(len(State.parameter['filtered'])):
        bullet_color = Style.GREEN if i == State.parameter['selection'] else Style.BRIGHT_BLACK
        line = (f'{bullet_color}  • {Style.DEFAULT}{State.parameter["filtered"][i][0]}'
                ' - '
                f'{State.parameter["filtered"][i][1].translation}')
        if i == State.parameter['selection']:
            line = Style.from_hex('#333', True) + line + ' ' + Style.DEFAULT_BG
        Term.insert(line, -5 - i)

    if first_time:
        Term.insert('    '
                    f'{Style.RED}[D]{Style.DEFAULT}elete, '
                    f'{Style.GREEN}[E]{Style.DEFAULT}dit, '
                    f'{Style.GREEN}[R]{Style.DEFAULT}eset selection', -5)
    elif State.parameter['selection'] == -1:
        Term.set_cursor(-2, len(State.parameter['promt']) + 5)


def explore_handle(k: Key):
    update_filtered = False
    if k == '/':
        State.state = State.Enum.MENU
        State.parameter = None
    elif k == Key.Special.ARROW_UP:
        if State.parameter['selection'] < len(State.parameter['filtered']) - 1:
            State.parameter['selection'] += 1
    elif k == Key.Special.ARROW_DOWN:
        if State.parameter['selection'] > -1:
            State.parameter['selection'] -= 1
    elif State.parameter['selection'] == -1:
        if k == Key.Special.TAB:
            State.explore_mode = 1 - State.explore_mode
            State.parameter['promt'] = ''
            State.parameter['selection'] = -1
            update_filtered = True
        elif k == Key.Special.BACKSPACE:
            if State.parameter['promt']:
                State.parameter['promt'] = State.parameter['promt'][:-1]
                update_filtered = True
        else:
            if State.explore_mode == State.Direction.REVERSE and k in en2ru:
                State.parameter['promt'] += en2ru[k]
            else:
                State.parameter['promt'] += str(k)
            update_filtered = True
    else:
        if k == 'd':
            del DB.data[State.parameter['filtered'][State.parameter['selection']][0]]
            update_filtered = True
            DB.dump()
        elif k == 'e':
            State.state = State.Enum.EDIT
        elif k == 'r':
            State.parameter['selection'] = -1
    if update_filtered:
        if State.parameter['promt']:
            State.parameter['filtered'] = sorted(
                filter(
                    lambda s: State.parameter['promt'].lower() in s[0].lower() + s[1].translation.lower(),
                    DB.data.items()),
                reverse=True)[:Term.in_height - 5]
        else:
            State.parameter['filtered'] = []
            State.parameter['selection'] = -1
        if State.parameter['selection'] >= len(State.parameter['filtered']):
            State.parameter['selection'] = len(State.parameter['filtered']) - 1


def edit_print():
    first_time = 'mod' not in State.parameter
    if first_time:
        phrase = State.parameter['filtered'][State.parameter['selection']]
        State.parameter['mod'] = phrase[0] + ' - ' + phrase[1].translation
        State.parameter['cursor'] = len(State.parameter['mod'])

    Term.insert(Style.BRIGHT_BLACK + '  ⮞ ' + State.parameter['promt'] + Style.DEFAULT, y=-3)
    if State.scroll_mode == State.Direction.STRAIGHT:
        tip = Style.BRIGHT_BLUE + 'Search'
    else:
        tip = Style.GREEN + 'Поиск'
    Term.insert('    ' + Style.BRIGHT_BLACK + tip + Style.DEFAULT, y=-2)

    for i in range(len(State.parameter['filtered'])):
        if State.parameter['selection'] == i:
            line = '  • ' + StrTool.format(State.parameter['mod'], colorize=True)
        else:
            line = Style.BRIGHT_BLACK + '  • ' + StrTool.format(
                State.parameter["filtered"][i][0] +
                ' - ' +
                State.parameter["filtered"][i][1].translation + Style.DEFAULT)
        Term.insert(line, -5 - i)

    cursor = State.parameter['cursor']
    Term.set_cursor(-4 - State.parameter['selection'], cursor + 5)


def edit_handle(k: Key):
    if k == '/':
        del State.parameter['mod']
        del State.parameter['cursor']
        State.state = State.Enum.EXPLORE
    elif k == Key.Special.ENTER:
        old_val = DB.data.pop(State.parameter['filtered'][State.parameter['selection']][0])
        kvp = State.parameter['mod'].split(' - ', 1)
        DB.data[kvp[0]] = Record(kvp[1], old_val.rate)
        DB.dump()

        if State.parameter['promt']:
            State.parameter['filtered'] = sorted(
                filter(
                    lambda s: State.parameter['promt'].lower() in s[0].lower() + s[1].translation.lower(),
                    DB.data.items()),
                reverse=True)[:Term.in_height - 5]
        else:
            State.parameter['filtered'] = []
            State.parameter['selection'] = -1
        if State.parameter['selection'] >= len(State.parameter['filtered']):
            State.parameter['selection'] = len(State.parameter['filtered']) - 1

        del State.parameter['mod']
        del State.parameter['cursor']
        State.state = State.Enum.EXPLORE
    elif k == Key.Special.BACKSPACE:
        if State.parameter['mod']:
            cursor = State.parameter['cursor']
            State.parameter['mod'] = State.parameter['mod'][:cursor - 1] + State.parameter['mod'][cursor:]
            State.parameter['cursor'] -= 1
    elif k == Key.Special.ARROW_LEFT:
        if State.parameter['cursor'] > 0:
            if ' - ' in State.parameter['mod'] and State.parameter['mod'].index(' - ') == State.parameter['cursor'] - 3:
                State.parameter['cursor'] -= 3
            else:
                State.parameter['cursor'] -= 1
    elif k == Key.Special.ARROW_RIGHT:
        if State.parameter['cursor'] < len(State.parameter['mod']):
            if ' - ' in State.parameter['mod'] and State.parameter['mod'].index(' - ') == State.parameter['cursor']:
                State.parameter['cursor'] += 3
            else:
                State.parameter['cursor'] += 1
    elif k == Key.Special.HOME:
        State.parameter['cursor'] = 0
    elif k == Key.Special.END:
        State.parameter['cursor'] = len(State.parameter['mod'])
    else:
        if ' - ' in State.parameter['mod'] and State.parameter['cursor'] >= State.parameter['mod'].index(' - ') + 3:
            c = en2ru[k]
        else:
            c = str(k)
        State.parameter['mod'] = (
                State.parameter['mod'][:State.parameter['cursor']] +
                c +
                State.parameter['mod'][State.parameter['cursor']:])
        State.parameter['cursor'] += 1


def scroll_print():
    first_time = State.parameter is None
    if first_time or not State.parameter['record']:
        State.parameter = {
            'phrase': '',
            'record': None,
            'reveal': False
        }
        Term.insert(
            f'{Style.GREEN}[Enter]{Style.DEFAULT} Scroll next / Correct',
            Term.in_height // 2 - 1,
            True)
        Term.insert(
            f'{Style.GREEN}[\']{Style.DEFAULT} Incorrect',
            Term.in_height // 2 + 1,
            True)
        return

    Term.insert(State.parameter['phrase'], Term.in_height // 2, True)
    if State.parameter['reveal']:
        Term.insert(Style.YELLOW + State.parameter['record'].translation + Style.DEFAULT, Term.in_height // 2 + 2, True)


def get_new_phrase():
    items = DB.data.items()
    rate_sum = 0
    for item in items:
        rate_sum += item[1].rate
    rnd = random.random() * rate_sum
    for item in items:
        if rnd < item[1].rate:
            break
        rnd -= item[1].rate
    State.parameter = {
        'phrase': item[0],
        'record': item[1],
        'reveal': False
    }


def scroll_handle(k: Key):
    if k == '/':
        State.state = State.Enum.MENU
        State.parameter = State.parameter['phrase']
    elif k == Key.Special.ENTER:
        if not State.parameter['reveal'] and State.parameter['record']:
            State.parameter['reveal'] = True
        else:
            if State.parameter['record']:
                State.parameter['record'].rate *= 0.75
                DB.dump()
            get_new_phrase()
    elif k == "'":
        if State.parameter['reveal'] and State.parameter['record']:
            State.parameter['record'].rate *= 1.25
            DB.dump()
            State.parameter['reveal'] = True
            get_new_phrase()


def main():
    DB.load()
    if not DEBUG:
        Term.clear()
    logic = {
        State.Enum.MENU: LogicBlock(menu_print, menu_handle),
        State.Enum.ADD: LogicBlock(add_print, add_handle),
        State.Enum.EXPLORE: LogicBlock(explore_print, explore_handle),
        State.Enum.EDIT: LogicBlock(edit_print, edit_handle),
        State.Enum.SCROLL: LogicBlock(scroll_print, scroll_handle)
    }

    State.state = State.Enum.MENU
    State.next_call = lambda: menu_print()
    Term.reset()
    while State.state != State.Enum.QUIT:
        logic[State.state].printer()
        Term.draw()
        c = Term.getch()
        State.first_time = State.state == State.Enum.MENU
        logic[State.state].handler(c)
        Term.reset()

    print(Style.RESET, end='')
    if not DEBUG:
        Term.clear()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        Term.clear()
        print(Style.RED + 'Error: \n' + Style.BRIGHT_BLACK)
        traceback.print_exception(e)
        print(Style.DEFAULT + '\nPress any key to exit...')
        Term.getch()
