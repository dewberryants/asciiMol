import os

_APP = os.path.abspath(os.path.dirname(__file__))
dir_data = os.path.join(_APP, "data")

data_atoms = {}
data_colors = {}

with open(os.path.join(dir_data, "atom_data")) as ifile:
    line = ifile.readline()
    while line != "":
        stripped = line.strip()
        if stripped.startswith("#"):
            pass
        elif stripped.startswith("C"):
            tmp = stripped.split()
            try:
                data_colors[tmp[1].upper()] = (float(tmp[2]), float(tmp[3]), float(tmp[4]), int(tmp[5]), int(tmp[6]))
            except (NameError, ValueError, KeyError):
                raise RuntimeError("DEFINITION FILE FORMAT ERROR (Colors)")
        elif stripped.startswith("A"):
            tmp = stripped.split()
            try:
                data_atoms[tmp[1].upper()] = (float(tmp[2]), tmp[3].upper())
            except (NameError, ValueError, KeyError):
                raise RuntimeError("DEFINITION FILE FORMAT ERROR (Covalent Radii)")
        line = ifile.readline()


def map_radii(a):
    for symbol in a:
        symbol = symbol.upper()
        if symbol in data_atoms:
            yield data_atoms[symbol][0]
        else:
            yield 1.5


def map_colors(a):
    for symbol in a:
        symbol = symbol.upper()
        if symbol in data_atoms:
            yield data_colors[data_atoms[symbol][1]]
        else:
            yield 0.9, 0.9, 0.9, 0, 0
