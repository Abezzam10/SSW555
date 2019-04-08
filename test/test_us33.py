""" US33: List Orphans
    Javer, Apr 8, 2019
"""

import os
import unittest
from gedcom_ajry import Gedcom

class test_us33(unittest.TestCase):
    """ Test cases for US33"""

    def test_list_living_single(self):
        expected = []
        result = Gedcom('./GEDCOM_files/integrated_no_err.ged').us33_list_orphans(debug=True)
        self.assertEqual(result_ids, expected)


if __name__ == '__main__':
    unittest.main(exit=False, verbosity=2)
