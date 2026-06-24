import unittest

from src.asciimol.app.io import read_xyz_block

class TestIO(unittest.TestCase):
    def test_read_xyz_block_valid(self):
        xyz_block = [
            "2",
            "comment line",
            "H 0.0 0.0 0.0",
            "H 0.0 0.0 1.0"
        ]
        expected_atms = [2]
        expected_pos = [[0.0, 0.0, 0.0], [0.0, 0.0, 1.0]]
        expected_sym = ["H", "H"]

        atms, pos, sym = read_xyz_block(xyz_block)

        self.assertEqual(atms, expected_atms)
        self.assertEqual(pos, expected_pos)
        self.assertEqual(sym, expected_sym)

    def test_read_xyz_block_invalid_atms(self):
        xyz_block = [
            "invalid",
            "comment line",
            "H 0.0 0.0 0.0"
        ]
        with self.assertRaises(ValueError):
            read_xyz_block(xyz_block)

    def test_read_xyz_block_malformed_line(self):
        xyz_block = [
            "1",
            "comment line",
            "H 0.0"
        ]
        with self.assertRaises(ValueError):
            read_xyz_block(xyz_block)

    def test_read_xyz_short(self):
        xyz_block = [
            "3",
            "comment line",
            "H 0.0 0.0 0.0"
        ]
        with self.assertRaises(ValueError):
            read_xyz_block(xyz_block)

    def test_read_xyz_long(self):
        xyz_block = [
            "1",
            "comment line",
            "H 0.0 0.0 0.0",
            "H 0.0 0.0 0.0",
            "H 0.0 0.0 0.0"
        ]
        with self.assertRaises(ValueError):
            read_xyz_block(xyz_block)

if __name__ == '__main__':
    unittest.main()
