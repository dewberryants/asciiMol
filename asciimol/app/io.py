try:
    from ase.data.pubchem import pubchem_atoms_search
    from ase.io import read
    use_ase = True
except ImportError:
    use_ase = False


def handle_io(input_string: str):
    if not use_ase:
        try:
            return read_xyz(input_string)
        except ValueError:
            print("ERROR: Could not read '%s' as .xyz file." % input_string)
            if input_string[-4:] != ".xyz":
                print("Consider installing ASE (pip install ase) for more formats!")
            return False, None, None
    else:
        try:
            atms = read(input_string)
        except FileNotFoundError:
            try:
                print("Searching '%s' on PubChem..." % input_string)
                atms = pubchem_atoms_search(smiles=input_string)
            except:
                print("ERROR: Argument does not seem to be an existing file or SMILES string.")
                return False, None, None
        return True, atms.get_positions(), atms.get_chemical_symbols()


def read_xyz(filename):
    with open(filename, "r") as handle:
        line = handle.readline()
        try:
            atms = int(line.strip())
        except ValueError:
            print("XYZ FORMAT ERROR: Could not read atom number.")
            raise ValueError
        pos, sym = [], []
        handle.readline()  # Unused Comment line
        for n in range(atms):
            if line == "":
                print("XYZ FORMAT ERROR: Unexpected EOF. Atoms and Atom Number in line 1 mismatch!")
                raise ValueError
            line = handle.readline()
            work = line.strip().split()
            try:
                sym.append(work[0])
                pos.append([float(work[1]), float(work[2]), float(work[3])])
            except IndexError:
                print("XYZ FORMAT ERROR: Line '%s' is not formatted correctly." % line)
                raise ValueError
        return True, pos, sym
