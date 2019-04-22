""" Ray, Apr 21
    US32: List all multiple births in a GEDCOM file
"""

import os
import unittest
from gedcom_ajry import Gedcom

class test_us31(unittest.TestCase):
    """ Test cases for US32"""

    def test_list_tripple_births(self):
        """Test case for tripple births"""
        expected_ids = [('@I6@','@I7@',{'@I9@','@I2@','@I8@'})]
        result = Gedcom('./GEDCOM_files/us32/tripplets_birth.ged').us32_list_multiple_births(debug=True)
        result_ids = []
        for indi in result:
            result_ids.append((indi.husb_id, indi.wife_id, indi.chil_id))
        self.assertEqual(result_ids, expected_ids)
    
    def test_list_twins_birth(self):
        """Test case for twin births"""
        expected_ids = [('@I2@','@I3@',{'@I1@','@I4@'})]
        result = Gedcom('./GEDCOM_files/us32/twin_birth.ged').us32_list_multiple_births(debug=True)
        result_ids = []
        for indi in result:
            result_ids.append((indi.husb_id, indi.wife_id, indi.chil_id))
        self.assertEqual(result_ids, expected_ids)
    
    def test_list_no_multiple_births(self):
        """Test case for no multiple births"""
        expected_ids = []
        result = Gedcom('./GEDCOM_files/us32/no_err.ged').us32_list_multiple_births(debug=True)
        result_ids = []
        for indi in result:
            result_ids.append((indi.husb_id, indi.wife_id, indi.chil_id))
        self.assertEqual(result_ids, expected_ids)
    


if __name__ == '__main__':
    unittest.main(exit=False, verbosity=2)