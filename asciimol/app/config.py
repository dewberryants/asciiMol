import argparse

from asciimol.app import map_colors, map_radii
from asciimol.app.colors import init_curses_color_pairs
from asciimol.app.io import handle_io


class Config:
    """
    The runtime configuration object. Contains currently opened file, as well as any other configurables.
    """

    def __init__(self):
        self.coordinates = None
        self.symbols = None
        self.colors = None
        self.bonds = None

    def parse(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('XYZFILE', metavar='XYZFILE or SMILES', type=str,
                            help='Specify an .xyz file or a SMILES string (e.g., CC) to open and display.')
        opts = parser.parse_args()
        proceed, self.coordinates, self.symbols = handle_io(opts.XYZFILE)
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
