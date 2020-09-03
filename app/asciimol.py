import argparse
import curses
from time import sleep

from app.renderer import Renderer


class AsciiMol:
    def __init__(self):
        self.stdscr = None
        self.renderer = None
        self.config = _Config()
        self.sig_changed = True

    def _redraw(self):
        self.stdscr.clear()
        self.draw_characters(self.renderer.content)
        self.stdscr.refresh()
        self.sig_changed = False

    def draw_characters(self, content: list):
        for i in range(curses.LINES - 1):
            for j in range(curses.COLS):
                self.stdscr.addstr(i, j, content[i][j])
        # Default status bar (navigation)
        self.stdscr.addstr(curses.LINES - 1, 0, " [Q] Quit")

    def _on_update(self):
        keys = []
        key = self.stdscr.getch()
        while key is not curses.ERR:
            keys.append(key)
            key = self.stdscr.getch()
        running = True
        if len(keys) > 0:
            # Q or q quits from anywhere, for now
            if 81 in keys or 113 in keys:
                running = False
        if self.sig_changed:
            self._redraw()
        return running

    def _mainloop(self, main_screen):
        # Save curses main screen for reference
        self.stdscr = main_screen
        # Init a new renderer of appropriate size
        self.renderer = Renderer(curses.LINES, curses.COLS, self.config)
        # Turns off cursor
        curses.curs_set(0)
        # Turns off hangup on input polling
        self.stdscr.nodelay(True)
        running = True
        while running:
            # Running at 25 fps
            sleep(0.04)
            running = self._on_update()

    def run(self):
        if self.config.proceed:
            curses.wrapper(self._mainloop)
        return 0


class _Config:
    def __init__(self):
        self.parser = self._setup_parser()
        opts = self.parser.parse_args()
        self.proceed, self.coordinates, self.symbols = self._parse_file(opts.XYZFILE)

    @staticmethod
    def _parse_file(name: str):
        pos, sym = None, None
        proceed = False
        if name is not None and name != "":
            with open(name, "r") as handle:
                proceed, pos, sym, = _Config._read_xyz(handle)
        return proceed, pos, sym

    @staticmethod
    def _setup_parser():
        parser = argparse.ArgumentParser()
        parser.add_argument('XYZFILE', type=str, help='Specify an .xyz file to open and display.')
        return parser

    @staticmethod
    def _read_xyz(handle):
        line = handle.readline()
        atms = -1
        try:
            atms = int(line.strip())
        except ValueError:
            print("XYZ FORMAT ERROR: Could not read atom number.")
            return False, None, None
        pos, sym = [], []
        handle.readline()  # Unused Comment line
        line = handle.readline()
        while line != "":
            work = line.strip().split()
            try:
                sym.append(work[0])
                pos.append([work[1], work[2], work[3]])
            except IndexError:
                print("XYZ FORMAT ERROR: Line '%s' is too short." % line)
                return False, None, None
            line = handle.readline()
        if atms == len(sym):
            return True, pos, sym
        else:
            print("XYZ FORMAT ERROR: Atom Number (%d) and actual data length (%d) mismatch!" % (atms, len(sym)))
            return False, None, None
