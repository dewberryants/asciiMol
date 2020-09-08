import curses


class ColorDict:
    def __init__(self):
        self.active = False
        self.dict = {}
        self._cdict = {}
        if curses.has_colors():
            curses.use_default_colors()
            from asciimol.app import data_colors, data_atoms
            # Init all the required color pairs that were defined in the data file
            cset = {}
            for n, clabel in enumerate(data_colors):
                r, g, b, x256, x8 = data_colors[clabel]
                col = x256 if curses.COLORS >= 256 else x8
                if col not in cset:
                    cset[col] = n
                try:
                    curses.init_pair(cset[col], col, -1)
                except curses.error:
                    raise RuntimeError("Could not init pair %d with color %d" % (cset[col], col))
                self._cdict[clabel] = cset[col]
            self.active = True
            # Translate all of the colors defined for the atom symbols to active curses ATTR
            self.dict = {}
            for key in data_atoms:
                col = data_atoms[key][1]
                if col in self._cdict:
                    self.dict[key] = str(curses.color_pair(self._cdict[col]))

    def __getitem__(self, item):
        if len(self.dict) == 0:
            return str(curses.color_pair(0))
        try:
            return self.dict[item]
        except (KeyError, ValueError):
            return str(curses.color_pair(0))

# Old Code for custom color palette -- does not work on xterm :(
#
# for n, key in enumerate(data_colors):
#     r, g, b = data_colors[key]
#     curses.init_color(n + 1, round(r * 1000), round(g * 1000), round(b * 1000))
#     curses.init_pair(n + 1, n + 1, curses.COLOR_BLACK)
#     self._cdict[key] = n + 1
# self.active = True
# # Translate all of the colors defined for the atom symbols to active curses ATTR
# self.dict = {}
# for key in data_atoms:
#     col = data_atoms[key][1]
#     if col in self._cdict:
#         self.dict[key] = str(curses.color_pair(self._cdict[col]))
