import argparse

import numpy as np

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
        self.atm_counts = None

    def parse(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('XYZFILE', metavar='XYZFILE or SMILES', type=str,
                            help='Specify an .xyz file or a SMILES string (e.g., CC) to open and display.')
        opts = parser.parse_args()
        self.atm_counts, self.coordinates, self.symbols = handle_io(opts.XYZFILE)
        self._setup_bonds()
        return self.atm_counts

    def post_setup(self):
        self._setup_colors()

    def _setup_bonds(self):
        if self.bonds:
            return
        self.bonds = list()
        offset = 0
        for n, counts in enumerate(self.atm_counts):
            radii = np.array(list(map_radii(self.symbols[offset:offset + counts])), dtype='float32')
            xyz = np.array(self.coordinates[offset:offset + counts], dtype='float32')
            rsq = (radii[..., np.newaxis] + radii + 0.41) ** 2
            dx = xyz[:, 0, np.newaxis] - xyz[:, 0]
            dy = xyz[:, 1, np.newaxis] - xyz[:, 1]
            dz = xyz[:, 2, np.newaxis] - xyz[:, 2]
            dsq = dx ** 2 + dy ** 2 + dz ** 2
            np.fill_diagonal(dsq, np.inf)
            bonds = np.argwhere(np.triu(dsq) < np.triu(rsq))
            bound = np.isin(np.arange(counts), bonds[:, 0]) + \
                np.isin(np.arange(counts), bonds[:, 1])
            unbound = np.hstack((np.argwhere(bound == 0), np.argwhere(bound == 0)))
            self.bonds.append(np.vstack((bonds, unbound)))
            offset += counts

    def _setup_colors(self):
        if self.colors:
            return
        colors = list(map_colors(self.symbols))
        self.colors = list(init_curses_color_pairs(colors))
