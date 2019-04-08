""" US31: List Living Single
    Javer, Apr 8, 2019
"""

import os
import unittest
from gedcom_ajry import Gedcom

class test_us31(unittest.TestCase):
    """ Test cases for US31"""

    def test_list_living_single(self):
        expected_ids = ["@I9@", "@I17@", "@I22@", "@I23@"]
        result = Gedcom('./GEDCOM_files/integrated_no_err.ged').us31_list_living_single(debug=True)
        result_ids = []
        for indi in result:
            result_ids.append(indi.indi_id)
        self.assertEqual(result_ids, expected_ids)

if __name__ == '__main__':
    unittest.main(exit=False, verbosity=2)
