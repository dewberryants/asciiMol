# asciiMOL

[![PyPI version](https://badge.fury.io/py/asciimol.svg)](https://badge.fury.io/py/asciimol)

![Screenshots](https://raw.githubusercontent.com/dewberryants/asciiMol/master/docs/animation.gif)

A basic molecule viewer written in Python, using curses; Thus, meant for linux terminals.

Features:

* Opening default cartesian .xyz files
* Orthographic view
* Navigation
* Zoom, Rotation, Auto-Rotation
* Bond detection and display
* Support for simple .xyz trajectories
* Optional integration of ASE and RDKit pypi packages for more formats and SMILES

## Installation

```sh
pip install asciimol
```

(Note: pip will install a run script in $HOME/.local/bin/ if you do not install with root permissions, so make sure this
directory is part of your $PATH.)

You can also run

```sh
pip install asciimol[formats,smiles]
```

to automatically install ASE for formats and RDKit for smiles.
