import json
import curses

screen = curses.initscr()
edge_y, edge_x = screen.getmaxyx()


class KeyCodes:
    ENTER = 10
    BACKSPACE = 8
    CTRL_BACKSPACE = 127


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

    @staticmethod
    def draw():
        title = 'Trans Dictionary'
        screen.addch(0, 0, Border.ARC_BR)
        screen.addch(0, edge_x - 1, Border.ARC_BL)
        screen.addch(edge_y - 1, 0, Border.ARC_TR)
        try:
            screen.addch(edge_y - 1, edge_x - 1, Border.ARC_TL)
        except curses.error:
            pass
        title_start_index = edge_x // 2 - len(title) // 2
        for x in list(range(1, title_start_index - 1)) + list(range(title_start_index + len(title) + 1, edge_x - 1)):
            screen.addstr(0, x, Border.HORIZ)
        for x in range(1, edge_x - 1):
            screen.addstr(edge_y - 1, x, Border.HORIZ)
        for y in range(1, edge_y - 1):
            screen.addstr(y, 0, Border.VERT)
            screen.addstr(y, edge_x - 1, Border.VERT)
        screen.addstr(0, title_start_index - 1, Border.CORNER_BL + title + Border.CORNER_BR)


MENU = (
    '╭─────────────┬─────────────╮',
    '│  Add Phrase │   Search    │',
    '│     [A]     │     [S]     │',
    '├─────────────┴─────────────┤',
    '│            Run            │',
    '│          [Enter]          │',
    '╰───────────────────────────╯'
)

with open("db.json", "r") as db_file:
    db = json.load(db_file)

curses.noecho()
curses.curs_set(0)

s = ''
c = ''
while s != 'q':
    screen.clear()
    Border.draw()
    for menu_y, menu_line in enumerate(MENU):
        screen.addstr(edge_y // 2 - len(MENU) // 2 + menu_y, edge_x // 2 - len(menu_line) // 2, menu_line)
    c = screen.getch()
    if c == KeyCodes.BACKSPACE:
        if len(s) > 0:
            s = s[:-1]
    else:
        s += chr(c)

curses.endwin()
