""" US31: List Living Single
    Javer, Apr 8, 2019
"""

import os
import unittest
from gedcom_ajry import Gedcom

class test_us31(unittest.TestCase):
    """ Test cases for US31"""

    def test_list_living_single(self):
        expected_ids = ['@I1@', '@I11@', '@I12@', '@I17@']
        result = Gedcom('./GEDCOM_files/us31/us31_living_single_age_over_30.ged').us31_list_living_single(debug=True)
        self.assertEqual(result, expected_ids)

if __name__ == '__main__':
    unittest.main(exit=False, verbosity=2)
