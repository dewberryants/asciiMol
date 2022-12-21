try:
    from ase.data.pubchem import pubchem_atoms_search
    from ase.io import read

    use_ase = True
except ImportError:
    use_ase = False

try:
    from rdkit.Chem import AllChem, MolFromSmiles, AddHs
    from rdkit.Chem.rdmolfiles import MolToXYZBlock

    use_rdkit = True
except ImportError:
    use_rdkit = False


def handle_io(input_string: str):
    if (not use_ase and not use_rdkit) or input_string[-4:] == ".xyz":
        try:
            with open(input_string, "r") as handle:
                return read_xyz(handle)
        except (ValueError, FileNotFoundError):
            print("ERROR: Could not read '%s' as .xyz file." % input_string)
            if input_string[-4:] != ".xyz":
                print("Consider installing the optional dependencies (ase, rdkit) for more formats!")
            return False, None, None
    elif use_ase and not use_rdkit:
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
    elif use_rdkit and not use_ase:
        try:
            with open(input_string, "r") as handle:
                return read_xyz(handle)
        except ValueError:
            print("ERROR: Could not read '%s' as xyz file." % input_string)
            return False
        except FileNotFoundError:
            proceed, pos, sym = read_smiles(input_string)
            if not proceed:
                print("ERROR: File '%s' not found and not a valid SMILES code!" % input_string)
                return False, None, None
            return proceed, pos, sym
    else:  # Using both
        try:
            atms = read(input_string)
            return True, atms.get_positions(), atms.get_chemical_symbols()
        except FileNotFoundError:
            proceed, pos, sym = read_smiles(input_string)
            if not proceed:
                print("ERROR: File '%s' not found and not a valid SMILES code!" % input_string)
                return False, None, None
            return proceed, pos, sym
        except KeyError:
            # ASE struggles to read XYZ files with invalid atom symbols
            # so try to read as xyz or fail
            try:
                with open(input_string, "r") as handle:
                    return read_xyz(handle)
            except (ValueError, FileNotFoundError):
                print("ERROR: ASE could not open '%s' and could not read '%s' as simple .xyz file." % input_string)


def read_smiles(smiles):
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
    for line in string_list[2:atms + 2]:
        work = line.strip().split()
        try:
            sym.append(work[0])
            pos.append([float(work[1]), float(work[2]), float(work[3])])
        except IndexError:
            print("XYZ FORMAT ERROR: Line '%s' is not formatted correctly." % line)
            raise ValueError
    return True, pos, sym
