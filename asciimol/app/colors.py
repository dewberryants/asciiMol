import curses


class ColorDict:
    def __init__(self):
        self.active = False
        if curses.has_colors():
            self.active = True
            symbols = ["O", "CL", "S", "N", "P", "C", "H"]
            colors = [curses.COLOR_RED, curses.COLOR_GREEN, curses.COLOR_YELLOW, curses.COLOR_BLUE,
                      curses.COLOR_MAGENTA, curses.COLOR_CYAN, curses.COLOR_WHITE]
            maxlen = curses.COLOR_PAIRS - 1
            self.dict = {}
            for n in range(len(symbols)):
                if n == maxlen:
                    break
                curses.init_pair(n + 1, colors[n], curses.COLOR_BLACK)
                self.dict[symbols[n]] = str(curses.color_pair(n + 1))

    def __getitem__(self, item):
        if self.dict is None:
            return str(curses.color_pair(0))
        try:
            return self.dict[item]
        except (KeyError, ValueError):
            return str(curses.color_pair(0))
