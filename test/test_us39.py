""" Ray, Apr 21
    US39: List all living couples in a GEDCOM file whose marriage anniversaries occur in the next 30 days
"""

import os
import unittest
from gedcom_ajry import Gedcom

class test_us31(unittest.TestCase):
    """ Test cases for US39"""

    def test_list_anniversaries(self):
        """Test case for listing upcoming anniversaries"""
        expected_ids = [('@I2@', '@I3@'),('@I6@', '@I7@')]
        result = Gedcom('./GEDCOM_files/us39/ann_in_30_days.ged').us39_list_anniversaries(debug=True)
        result_ids = []
        for indi in result:
            result_ids.append((indi.husb_id, indi.wife_id))
        self.assertEqual(result_ids, expected_ids)
    
    def test_list_no_anniversaries(self):
        """Test case for no upcoming anniversaries"""
        expected_ids = []
        result = Gedcom('./GEDCOM_files/us39/no_err.ged').us39_list_anniversaries(debug=True)
        result_ids = []
        for indi in result:
            result_ids.append((indi.husb_id, indi.wife_id))
        self.assertEqual(result_ids, expected_ids)
    


if __name__ == '__main__':
    unittest.main(exit=False, verbosity=2)