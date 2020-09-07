import os

_APP = os.path.abspath(os.path.dirname(__file__))
dir_data = os.path.join(_APP, "data")

data_radii = {}
with open(os.path.join(dir_data, "covalent_radii")) as ifile:
    line = ifile.readline()
    while line != "":
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        tmp = stripped.split()
        assert (len(tmp) == 2), "DATA FORMAT ERROR (Covalent Radii)"
        try:
            data_radii[tmp[0].upper()] = float(tmp[1])
        except (NameError, ValueError, KeyError):
            raise RuntimeError("DATA FORMAT ERROR (Covalent Radii)")
        line = ifile.readline()
