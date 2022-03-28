import curses
from math import ceil
from time import sleep

from asciimol.app.renderer import Renderer
from asciimol.app.config import Config


class AsciiMol:
    def __init__(self):
        self.stdscr = None
        self.renderer = None
        self.sig_changed = True
        self.config = Config()
        self.frames = 0
        self.timeout = 0

    def redraw(self):
        self.stdscr.clear()
        self.draw_characters(self.renderer.content)
        self.draw_navbar()
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
        navbar_string = "[Q]uit [R]eset "
        navbar_string += "[B]onds %s " % ("on " if self.renderer.btoggle else "off")
        navbar_string += "[+-] Zoom (%- 3.3f) " % self.renderer.zoom
        navbar_string += "[↔↕] Rotate (%-3.f, %-3.f, %-3.f) " % (x, y, z)
        navbar_string += "[Z] ↔ Y/Z rotation (%s) " % ztoggle_str
        navbar_string += "[WSAD] Navigate "
        navbar_string += "[C] Center "
        navbar_string += "[T] Principle Axes "
        navbar_string += "[F1-3] Auto-Rotate"
        try:
            self.stdscr.addstr(navbar_string)
        except curses.error:
            if curses.LINES > 1 and curses.COLS > 3:
                self.stdscr.addstr(curses.LINES - 1, curses.COLS - 4, "...")

    def handle_keypresses(self, keys):
        self.sig_changed = False
        if len(keys) > 0:
            if 87 in keys or 119 in keys:  # W
                self.sig_changed = self.renderer.navigate(dy=-ceil(self.renderer.zoom))
            if 83 in keys or 115 in keys:  # S
                self.sig_changed = self.renderer.navigate(dy=ceil(self.renderer.zoom))
            if 65 in keys or 97 in keys:  # A
                self.sig_changed = self.renderer.navigate(dx=-ceil(self.renderer.zoom))
            if 68 in keys or 100 in keys:  # D
                self.sig_changed = self.renderer.navigate(dx=ceil(self.renderer.zoom))
            if 67 in keys or 99 in keys:  # C
                self.sig_changed = self.renderer.center()
            if 84 in keys or 116 in keys:  # T
                self.sig_changed = self.renderer.prinicple_axes()
            if curses.KEY_F1 in keys:
                self.renderer.toggle_auto_rotate(x=True)
            if curses.KEY_F2 in keys:
                self.renderer.toggle_auto_rotate(y=True)
            if curses.KEY_F3 in keys:
                self.renderer.toggle_auto_rotate(z=True)
            if curses.KEY_DOWN in keys:
                self.sig_changed = self.renderer.rotate(x=1)
            if curses.KEY_UP in keys:
                self.sig_changed = self.renderer.rotate(x=-1)
            if curses.KEY_LEFT in keys:
                self.sig_changed = self.renderer.rotate(z=1) if self.renderer.ztoggle else self.renderer.rotate(y=1)
            if curses.KEY_RIGHT in keys:
                self.sig_changed = self.renderer.rotate(z=-1) if self.renderer.ztoggle else self.renderer.rotate(y=-1)
            if 43 in keys:  # +
                self.sig_changed = self.renderer.modify_zoom(0.1)
            if 45 in keys:  # -
                self.sig_changed = self.renderer.modify_zoom(-0.1)
            if 82 in keys or 114 in keys:  # R
                self.sig_changed = self.renderer.reset_view()
            if 66 in keys or 98 in keys:  # B
                self.renderer.btoggle = not self.renderer.btoggle
                self.sig_changed = True
            if 90 in keys or 122 in keys:  # Z
                self.renderer.ztoggle = not self.renderer.ztoggle
                self.sig_changed = True
            if 81 in keys or 113 in keys:  # Q
                return False
        return True

    def on_update(self):
        keys = []
        key = self.stdscr.getch()
        while key is not curses.ERR:
            keys.append(key)
            key = self.stdscr.getch()
        running = self.handle_keypresses(keys)
        # Limit resizing to once per second, this is easier on curses.
        if self.frames == 59:
            if curses.is_term_resized(self.renderer.height, self.renderer.width):
                curses.update_lines_cols()
                self.renderer.resize(curses.LINES, curses.COLS)
                self.sig_changed = True
            self.frames = 0
        # Auto-Rotation at 30 fps to reduce workload
        if self.renderer.get_auto_rotate() and self.frames % 2 == 0:
            self.renderer.auto_rotate()
            self.sig_changed = True
        if self.sig_changed:
            try:
                self.renderer.buffer_scene()
                self.redraw()
                self.timeout = 0
            except curses.error:
                # Try again next update, this could hang, so do a timeout counter
                self.timeout += 1
        if self.timeout > 100:
            raise RuntimeError("Curses had an irrecoverable problem.")
        self.frames += 1
        return running

    def main_loop(self, main_screen):
        # The internal color setup requires curses to be initialized first
        self.config.post_setup()
        # Save curses main screen for reference
        self.stdscr = main_screen
        # Init a new renderer of appropriate size
        self.renderer = Renderer(curses.LINES, curses.COLS, self.config)
        # Turns off cursor
        curses.curs_set(0)
        # Turns off hangup on input polling
        self.stdscr.nodelay(True)
        running = True
        self.redraw()
        while running:
            try:
                # Running at 60 fps
                sleep(1 / 60)
                running = self.on_update()
            except (KeyboardInterrupt, SystemError, SystemExit):
                running = False

    def run(self):
        if self.config.parse():
            curses.wrapper(self.main_loop)
        return 0
