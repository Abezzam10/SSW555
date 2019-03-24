""" Ray, <Mar 24, 2019>
    US23: Unique name and birth date
    <No more than one individual with the same name and birth date should appear in a GEDCOM file>
"""

import unittest
from gedcom_ajry import Gedcom

class test_us23(unittest.TestCase):
    """ Test cases for US23"""

    def test_all_unique_name_birthdate(self):
        """ None of the individual has same name or birthdate"""
        ged = Gedcom('./GEDCOM_files/us23/no_err.ged')
        self.assertEqual(ged.us23_unique_name_and_birt(debug=True), [])

    def test_same_name(self):
        """ Two individuals have same name"""
        ged = Gedcom('./GEDCOM_files/us23/same_name.ged')
        expected = [
            ('@I1@', '@I2@')
        ]
        self.assertEqual(ged.us23_unique_name_and_birt(debug=True), expected)
    
    def test_same_birthdate(self):
        """ Two individuals have same birth date"""
        ged = Gedcom('./GEDCOM_files/us23/same_birthdate.ged')
        expected = [
            ('@I3@', '@I4@')
        ]
        self.assertEqual(ged.us23_unique_name_and_birt(debug=True), expected)
    
    def test_same_name_birthdate(self):
        """ Two individuals have same name and birth date"""
        ged = Gedcom('./GEDCOM_files/us23/same_name_birthdate.ged')
        expected = [
            ('@I6@', '@I7@')
        ]
        self.assertEqual(ged.us23_unique_name_and_birt(debug=True), expected)


if __name__ == '__main__':
    unittest.main(exit=False, verbosity=2)
    
