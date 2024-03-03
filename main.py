import json
import curses


class KeyCodes:
    ENTER = 10
    BACKSPACE = 8
    CTRL_BACKSPACE = 127


with open("db.json", "r") as db_file:
    db = json.load(db_file)

screen = curses.initscr()
curses.noecho()
curses.curs_set(0)

s = ''
while s != 'q':
    c = screen.getch()
    if c == KeyCodes.BACKSPACE:
        if len(s) > 0:
            s = s[:-1]
    else:
        s += chr(c)
    screen.clear()
    screen.addstr(0, 0, s + f' ({len(s)})')
    screen.addstr(1, 0, str(c))

curses.endwin()
