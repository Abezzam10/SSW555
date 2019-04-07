""" Ray, Apr 7th, 2019,
    US18: Siblings should not marry
    Siblings should not marry one another
"""

import unittest
from gedcom_ajry import Gedcom

class test_us18(unittest.TestCase):
    """ Test cases for US23"""

    def test_no_siblings_married(self):
        """ None of the individual has same name or birthdate"""
        ged = Gedcom('./GEDCOM_files/us18/no_err.ged')
        self.assertEqual(ged.us18_siblings_should_not_marry(debug=True), [])

    # def test_same_name(self):
    #     """ Two individuals have same name"""
    #     ged = Gedcom('./GEDCOM_files/us23/same_name.ged')
    #     expected = []
    #     self.assertEqual(ged.us23_unique_name_and_birt(debug=True), expected)
    
    # def test_same_birthdate(self):
    #     """ Two individuals have same birth date"""
    #     ged = Gedcom('./GEDCOM_files/us23/same_birthdate.ged')
    #     expected = []
    #     self.assertEqual(ged.us23_unique_name_and_birt(debug=True), expected)
    
    def test_same_name_birthdate(self):
        """ Two siblings are in the same marriage"""
        ged = Gedcom('./GEDCOM_files/us18/test_siblings_married.ged')
        expected = [
            ('@I1@', '@I4@'), ('@I4@', '@I1@')
        ]
        self.assertEqual(ged.us18_siblings_should_not_marry(debug=True), expected)


if __name__ == '__main__':
    unittest.main(exit=False, verbosity=2)
    
