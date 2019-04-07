""" US28: Order siblings by age
    Benji, Feb 24th, 2019
"""

import os
import unittest
from gedcom_ajry import Gedcom

class test_us28(unittest.TestCase):
    """ Test cases for US28"""

    def test_diff_name_diff_birt(self):
        """Sort the siblings with different names and birth dates (no twins)"""
        expected = {('@F1@', 'Rogan'): [('@I3@', 24, 'Sataglo'), ('@I4@', 23, 'Jassica'), ('@I5@', 22, 'Julia'), ('@I6@', 21, 'Jane'), ('@I7@', 20, 'Slovikansky')]}
        self.assertEqual(
            Gedcom('./GEDCOM_files/us28/us28_diff_name_diff_birth.ged').us28_order_siblings_by_age(debug=True),
            expected
        )

    def test_diff_name_same_birt(self):
        """Sort the siblings with different names BUT same birth dates (twins)"""
        expected = {('@F1@', 'Rogan'): [('@I3@', 24, 'Sataglo'), ('@I5@', 22, 'Julia'), ('@I4@', 22, 'Jassica'), ('@I6@', 22, 'Jane'), ('@I7@', 20, 'Slovikansky')]}
        self.assertEqual(
            Gedcom('./GEDCOM_files/us28/us28_diff_name_same_birth.ged').us28_order_siblings_by_age(debug=True),
            expected
        )

if __name__ == '__main__':
    unittest.main(exit=False, verbosity=2)
