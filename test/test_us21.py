""" Ray, Apr 7th, 2019,
    US21: Correct gender for role
    Husband in family should be male and wife in family should be female
"""

import unittest
from gedcom_ajry import Gedcom

class test_us21(unittest.TestCase):
    """ Test cases for US21"""

    def test_all_correct_gender(self):
        """ All the individual have correct gender roles"""
        ged = Gedcom('./GEDCOM_files/us21/no_err.ged')
        self.assertEqual(ged.us21_correct_gender_for_role(debug=True), [])
    
    def test_husb_female(self):
        """ Husband has the gender female"""
        ged = Gedcom('./GEDCOM_files/us21/test_husb_female.ged')
        expected = [
            ('@I2@')
        ]
        self.assertEqual(ged.us21_correct_gender_for_role(debug=True), expected)
    
    def test_wife_male(self):
        """Wife has the gender male"""
        ged = Gedcom('./GEDCOM_files/us21/test_wife_male.ged')
        expected = [
            ('@I3@')
        ]
        self.assertEqual(ged.us21_correct_gender_for_role(debug=True), expected)
    
    def test_wife_male_husb_female(self):
        """Wife has the gender male and husband has gender female"""
        ged = Gedcom('./GEDCOM_files/us21/test_wife_male_husb_female.ged')
        expected = [
            '@I2@', '@I3@'
        ]
        self.assertEqual(ged.us21_correct_gender_for_role(debug=True), expected)
    
    


if __name__ == '__main__':
    unittest.main(exit=False, verbosity=2)
    
