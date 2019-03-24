""" Ray, <Mar 24, 2019>
    US08: Birth before marriage of parents
    <Children should be born after marriage of parents (and not more than 9 months after their divorce)>
"""

import unittest
from gedcom_ajry import Gedcom

class test_us08(unittest.TestCase):
    """ Test cases for US08"""

    def test_birth_after_marr(self):
        """ Birth of all the children after marriage"""
        ged = Gedcom('./GEDCOM_files/us08/birth_after_marr.ged')
        self.assertEqual(ged.us08_birt_b4_marr_of_par(debug=True), [])

    def test_birth_before_marr(self):
        """ Birth of a child before the marriage"""
        ged = Gedcom('./GEDCOM_files/us08/birth_before_marr.ged')
        expected = [
            ('@F3@', '@I15@', '@I16@')
        ]
        self.assertEqual(ged.us08_birt_b4_marr_of_par(debug=True), expected)
    
    def test_birth_after_9_div(self):
        """ Birth of a child 9 months after the divorce"""
        ged = Gedcom('./GEDCOM_files/us08/birth_after_9_div.ged')
        expected = [
            ('@F7@', '@I10@', '@I12@')
        ]
        self.assertEqual(ged.us08_birt_b4_marr_of_par(debug=True), expected)
    
    def test_birth_before_9_div(self):
        """ Birth of a child 9 months before the divorce"""
        ged = Gedcom('./GEDCOM_files/us08/birth_before_9_div.ged')
        self.assertEqual(ged.us08_birt_b4_marr_of_par(debug=True), [])


if __name__ == '__main__':
    unittest.main(exit=False, verbosity=2)
    
