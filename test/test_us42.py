""" US42: Reject the illegitimate datetime
    Benji, Apr 21st, 2019
"""

import os
import unittest
from gedcom_ajry import Gedcom

class test_us42(unittest.TestCase):
    """ Test cases for US27"""
    def test_date_out_of_range(self):
        """test if datetime out of range (e.g. Feb 30th)"""
        with self.assertRaises(ValueError):
            Gedcom('GEDCOM_files/us42/us42_date_out_of_range.ged')
    
    def test_wrong_fmt(self):
        """test if datetime is given with wrong format (e.g. 1994-01-01)"""
        with self.assertRaises(ValueError):
            Gedcom('GEDCOM_files/us42/us42_date_wrong_fmt.ged')
    
if __name__ == '__main__':
    unittest.main(exit=False, verbosity=2)
    