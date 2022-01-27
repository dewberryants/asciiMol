import argparse

from asciimol.app import map_colors, map_radii
from asciimol.app.colors import init_curses_color_pairs


class Config:
    """
    The runtime configuration object. This is meant to be used as a singleton.
    Contains currently opened file, as well as any other configurables.
    """

    def __init__(self):
        self.coordinates = None
        self.symbols = None
        self.colors = None
        self.bonds = None

    def parse(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('XYZFILE', type=str, help='Specify an .xyz file to open and display.')
        opts = parser.parse_args()
        with open(opts.XYZFILE, "r") as xyzfile:
            proceed, self.coordinates, self.symbols = read_xyz(xyzfile)
        return proceed

    def post_setup(self):
        self._setup_bonds()
        self._setup_colors()

    def _setup_bonds(self):
        if self.bonds:
            return
        atms = len(self.symbols)
        radii = list(map_radii(self.symbols))
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
        self.bonds = bonds

    def _setup_colors(self):
        if self.colors:
            return
        colors = list(map_colors(self.symbols))
        self.colors = list(init_curses_color_pairs(colors))


def read_xyz(handle):
    line = handle.readline()
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


conf = Config()

__all__ = [conf]
