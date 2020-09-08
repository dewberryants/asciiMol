import argparse
import curses
from time import sleep

from asciimol.app import data_atoms
from asciimol.app.colors import ColorDict
from asciimol.app.renderer import Renderer


class AsciiMol:
    def __init__(self):
        self.stdscr = None
        self.renderer = None
        self.config = _Config()
        self.sig_changed = True
        self.frames = 0
        self.timeout = 0

    def _redraw(self):
        self.stdscr.clear()
        self.draw_characters(self.renderer.content)
        self.stdscr.refresh()
        self.sig_changed = False

    def draw_characters(self, content: list):
        for i in range(curses.LINES - 2):
            for j in range(curses.COLS):
                char, col = content[i][j].split(",")
                self.stdscr.addstr(i, j, char, int(col))

    def draw_navbar(self):
        x, y, z = self.renderer.rotcounter
        ztoggle_str = "Z" if self.renderer.ztoggle else "Y"
        navbar_string = "[Q]uit [R]eset View"
        navbar_string += " [B]onds %s " % ("on " if self.renderer.btoggle else "off")
        navbar_string += "[+-] Zoom (%- 3.3f) " % self.renderer.zoom
        navbar_string += "[↔↕] Rotate (%-3.f, %-3.f, %-3.f) " % (x, y, z)
        navbar_string += "[Z] ↔ Y/Z rotation (%s) " % ztoggle_str
        navbar_string += " [WSAD] Navigate"
        try:
            self.stdscr.addstr(navbar_string)
        except curses.error:
            if curses.LINES > 1 and curses.COLS > 3:
                self.stdscr.addstr(curses.LINES - 1, curses.COLS - 4, "...")

    def _on_update(self):
        keys = []
        key = self.stdscr.getch()
        while key is not curses.ERR:
            keys.append(key)
            key = self.stdscr.getch()
        running = True
        if len(keys) > 0:
            if 87 in keys or 119 in keys:  # W
                self.renderer.m = (self.renderer.m[0], self.renderer.m[1] - round(self.renderer.zoom))
                self.sig_changed = self.renderer.draw_scene()
            if 83 in keys or 115 in keys:  # S
                self.renderer.m = (self.renderer.m[0], self.renderer.m[1] + round(self.renderer.zoom))
                self.sig_changed = self.renderer.draw_scene()
            if 65 in keys or 97 in keys:  # A
                self.renderer.m = (self.renderer.m[0] - round(self.renderer.zoom), self.renderer.m[1])
                self.sig_changed = self.renderer.draw_scene()
            if 68 in keys or 100 in keys:  # D
                self.renderer.m = (self.renderer.m[0] + round(self.renderer.zoom), self.renderer.m[1])
                self.sig_changed = self.renderer.draw_scene()
            if curses.KEY_DOWN in keys:
                self.renderer.rotate(1)
                self.sig_changed = self.renderer.draw_scene()
            if curses.KEY_UP in keys:
                self.renderer.rotate(-1)
                self.sig_changed = self.renderer.draw_scene()
            if curses.KEY_LEFT in keys:
                self.renderer.rotate(2)
                self.sig_changed = self.renderer.draw_scene()
            if curses.KEY_RIGHT in keys:
                self.renderer.rotate(-2)
                self.sig_changed = self.renderer.draw_scene()
            if 43 in keys:  # +
                self.renderer.zoom += 0.1
                self.sig_changed = self.renderer.draw_scene()
            if 45 in keys and self.renderer.zoom > 0.2:  # -
                self.renderer.zoom -= 0.1
                self.sig_changed = self.renderer.draw_scene()
            if 82 in keys or 114 in keys:  # R
                self.renderer.reset_view()
                self.sig_changed = self.renderer.draw_scene()
            if 66 in keys or 98 in keys:  # B
                self.renderer.btoggle = not self.renderer.btoggle
                self.sig_changed = self.renderer.draw_scene()
            if 90 in keys or 122 in keys:  # Z
                self.renderer.ztoggle = not self.renderer.ztoggle
                self.sig_changed = self.renderer.draw_scene()
            # Q or q quits from anywhere, for now
            if 81 in keys or 113 in keys:
                running = False
        # Limit resizing to once per second, this is easier on curses.
        if self.frames == 49:
            if curses.is_term_resized(self.renderer.height, self.renderer.width):
                curses.update_lines_cols()
                self.renderer.resize(curses.LINES, curses.COLS)
                self.sig_changed = self.renderer.draw_scene()
            self.frames = 0
        if self.sig_changed:
            try:
                self._redraw()
                self.draw_navbar()
                self.timeout = 0
            except curses.error:
                # Try again next update, this could hang, so do a timeout counter
                self.timeout += 1
        if self.timeout > 100:
            raise RuntimeError("Curses had an irrecoverable problem.")
        self.frames += 1
        return running

    def _mainloop(self, main_screen):
        # Save curses main screen for reference
        self.stdscr = main_screen
        self.config.colors = ColorDict()
        # Init a new renderer of appropriate size
        self.renderer = Renderer(curses.LINES, curses.COLS, self.config)
        # Turns off cursor
        curses.curs_set(0)
        # Turns off hangup on input polling
        self.stdscr.nodelay(True)
        running = True
        while running:
            try:
                # Running at 50 fps
                sleep(0.02)
                running = self._on_update()
            except (KeyboardInterrupt, SystemError, SystemExit):
                running = False

    def run(self):
        if self.config.proceed:
            curses.wrapper(self._mainloop)
            curses.use_default_colors()
        return 0


class _Config:
    def __init__(self):
        self.parser = self._setup_parser()
        opts = self.parser.parse_args()
        self.proceed, self.coordinates, self.symbols = self._parse_file(opts.XYZFILE)
        if self.proceed:
            self.bonds = self._setup_bonds()
        self.colors = None

    def _setup_bonds(self):
        atms = len(self.symbols)
        radii = list(self._map_radii(self.symbols))
        bonds = []
        unbound = list(range(atms))
        for i in range(atms):
            for j in range(i):
                xa, ya, za = self.coordinates[i]
                xb, yb, zb = self.coordinates[j]
                rsq = (radii[i] + radii[j] + 0.41) ** 2
                dist = (xa - xb) ** 2 + (ya - yb) ** 2 + (za - zb) ** 2
                if dist < rsq or dist < 0.4:
                    bonds.append((i, j))
                    unbound[i] = -1
                    unbound[j] = -1
        for n, state in enumerate(unbound):
            if state != -1:
                bonds += [(n, n)]
        return bonds

    @staticmethod
    def _map_radii(a):
        for symbol in a:
            if symbol in data_atoms:
                yield data_atoms[symbol][0]
            else:
                yield 1.5

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
                pos.append([float(work[1]), float(work[2]), float(work[3])])
            except IndexError:
                print("XYZ FORMAT ERROR: Line '%s' is too short." % line)
                return False, None, None
            line = handle.readline()
        if atms == len(sym):
            return True, pos, sym
        else:
            print("XYZ FORMAT ERROR: Atom Number (%d) and actual data length (%d) mismatch!" % (atms, len(sym)))
            return False, None, None
