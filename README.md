# asciiMOL

[![PyPI version](https://badge.fury.io/py/asciimol.svg)](https://badge.fury.io/py/asciimol)

![Screenshots](https://raw.githubusercontent.com/dewberryants/asciiMol/master/docs/anim.gif)

A basic molecule viewer written in Python, using curses; Thus, meant for linux terminals.

This is an alpha version, featuring:

* Opening default cartesian .xyz files
* Displaying one-letter atom labels
* Orthographic view
* Navigation
* Zoom, Rotation, Auto-Rotation
* Bond detection and display
* Optional integration of ASE and RDKit pypi packages for more formats and SMILES

## Installation

```sh
pip install asciimol
```

(Note: pip will install a run script in $HOME/.local/bin/ if you do not install with root permissions, so make sure this
directory is part of your $PATH.)

You can also run

```sh
pip install asciimol\[formats,smiles\]
```

to automatically install ASE for formats and RDKit for smiles.