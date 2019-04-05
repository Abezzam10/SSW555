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
       
        ged = Gedcom('./GEDCOM_files/us02/us02_mar_after_birt.ged')
        self.assertEqual(ged.us02_birth_before_marriage(debug=True), [])
    
    def test_mar_before_birt(self):
        """ Marriage before birth"""
       
        ged = Gedcom('./GEDCOM_files/us02/us02_mar_before_birt.ged')
        self.assertEqual(
            ged.us02_birth_before_marriage(debug=True), 
            [('husband', '08/06/3169', '@F1@', 'Oswaldo Mccarthy', '@I2@', '01/01/1992')]
            )
    
    def test_mar_on_birt_wife(self):
        """ Marriage is on the birth date"""
       
        ged = Gedcom('./GEDCOM_files/us02/us02_mar_on_birt.ged')
        self.assertEqual(
            ged.us02_birth_before_marriage(debug=True),
            [('wife', '04/17/1972', '@F1@', 'Sherika Ault', '@I3@', '08/06/1969')]
            )
        

if __name__ == '__main__':
    unittest.main(exit=False, verbosity=2)
    
