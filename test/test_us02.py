""" Ray, Feb 22th, 2019
    US02: Birth before marriage
    Birth should occur before marriage of an individual
"""

import unittest
from gedcom_ajry import Gedcom

class test_us02(unittest.TestCase):
    """ Test cases for US02"""

    def test_mar_after_birt(self):
        """ Marriage is after birth"""
       
        ged = Gedcom('./GEDCOM_files/us02_mar_after_birt.ged')
        self.assertEqual(ged.us02_birth_before_marriage(), True)
    
    def test_mar_before_birt_husb(self):
        """ Marriage is before birth of Husband"""
       
        ged = Gedcom('./GEDCOM_files/us02_mar_before_birt.ged')
        self.assertEqual(ged.us02_birth_before_marriage(), False)
    
    def test_mar_before_birt_wife(self):
        """ Marriage is before birth of Wife"""
       
        ged = Gedcom('./GEDCOM_files/us02_mar_before_birt.ged')
        self.assertEqual(ged.us02_birth_before_marriage(), False)
    
    def test_mar_on_birt_wife(self):
        """ Marriage is on the birth date"""
       
        ged = Gedcom('./GEDCOM_files/us02_mar_on_birt.ged')
        self.assertEqual(ged.us02_birth_before_marriage(), False)
        

if __name__ == '__main__':
    unittest.main(exit=False, verbosity=2)
    
