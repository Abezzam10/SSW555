""" US33: List Orphans
    Javer, Apr 8, 2019
"""

import os
import unittest
from gedcom_ajry import Gedcom

class test_us33(unittest.TestCase):
    """ Test cases for US33"""

    def test_list_orphans_less_than_18(self):
        expected = [("@F7@", "@I14@")]
        result = Gedcom('./GEDCOM_files/us33/us33_ophaned_children_less_than_18.ged').us33_list_orphans(debug=True)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main(exit=False, verbosity=2)
