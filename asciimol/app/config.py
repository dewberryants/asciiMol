import argparse

from asciimol.app import map_colors, map_radii
from asciimol.app.colors import init_curses_color_pairs


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
        try:
            with open(opts.XYZFILE, "r") as handle:
                proceed, self.coordinates, self.symbols = read_xyz(handle)
        except ValueError:
            print("ERROR: Could not read '%s' as xyz file." % opts.XYZFILE)
            return False
        except FileNotFoundError:
            proceed, self.coordinates, self.symbols = read_smiles(opts.XYZFILE)
            if not proceed:
                print("ERROR: File '%s' not found and not a valid SMILES code!" % opts.XYZFILE)
                return False
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


def read_smiles(smiles):
    from rdkit.Chem import AllChem, MolFromSmiles, AddHs
    from rdkit.Chem.rdmolfiles import MolToXYZBlock
    mol = MolFromSmiles(smiles)
    if mol is None:
        return False, None, None
    mol = AddHs(mol)
    AllChem.EmbedMolecule(mol)
    try:
        return read_xyz_block(MolToXYZBlock(mol).strip().split("\n"))
    except ValueError:
        return False, None, None


def read_xyz(handle):
    content = handle.readlines()
    try:
        return read_xyz_block(content)
    except ValueError:
        return False, None, None


def read_xyz_block(string_list):
    try:
        atms = int(string_list[0])
    except ValueError:
        print("XYZ FORMAT ERROR: Could not read atom number.")
        raise ValueError
    pos, sym = [], []
    for line in string_list[2:atms+2]:
        work = line.strip().split()
        try:
            sym.append(work[0])
            pos.append([float(work[1]), float(work[2]), float(work[3])])
        except IndexError:
            print("XYZ FORMAT ERROR: Line '%s' is not formatted correctly." % line)
            raise ValueError
    return True, pos, sym