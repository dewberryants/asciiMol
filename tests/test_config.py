import unittest

from src.asciimol.app.config import Config, _setup_bond_block

class TestConfig(unittest.TestCase):
    def test_setup_config(self):
        self.assertIsNotNone(Config())

    def test_setup_bonds(self):
        mock_symbols = ["O", "H", "H"]
        mock_coords = [
            [0, 0, 0],
            [0, 0.75545, -0.75545],
            [0.11779, -0.47116, -0.47116]
        ]
        result = _setup_bond_block(mock_symbols, mock_coords, 0, 3)
        self.assertListEqual(result.tolist(), [[0, 1], [0, 2]])
