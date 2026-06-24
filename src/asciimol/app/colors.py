import curses


def init_curses_color_pairs(a):
    if curses.has_colors():
        curses.use_default_colors()
        # Lazily init only colors as color pairs that are actually needed
        pair = 1
        cdict = dict()
        for entry in a:
            r, g, b, x256, x8 = entry
            col = x256 if curses.COLORS >= 256 else x8
            if str(col) not in cdict:
                try:
                    curses.init_pair(pair, col, -1)
                    cdict[str(col)] = pair
                    pair += 1
                except curses.error:
                    raise RuntimeError("Could not init pair %d with color %d" % (pair, col))
            yield str(curses.color_pair(cdict[str(col)]))
    else:
        return ["0"] * len(a)
