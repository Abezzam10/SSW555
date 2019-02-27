""" Ray, Feb 22th, 2019
    US11: No bigamy
    Married person should not be in another marriage
"""

import unittest
from gedcom_ajry import Gedcom

class test_us11(unittest.TestCase):
    """ Test cases for US11"""

    
    def test_wife_two_marr(self):
        """ Wife is involved in multiple marriages"""
       
        ged = Gedcom('./GEDCOM_files/proj01.ged')
        self.assertEqual(ged.us11_no_bigamy(), False)
    
    def test_no_bigamy(self):
        """ None of the spouses are involved in multiple marriages"""
       
        ged = Gedcom('./GEDCOM_files/test04.ged')
        self.assertEqual(ged.us11_no_bigamy(), True)
    
    def test_husb_two_marr(self):
        """ Husband is involved in multiple marriages"""
       
        ged = Gedcom('./GEDCOM_files/us11/us11_no_bigamy.ged')
        self.assertEqual(ged.us11_no_bigamy(), False)
        

if __name__ == '__main__':
    unittest.main(exit=False, verbosity=2)
    
