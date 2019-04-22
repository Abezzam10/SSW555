""" US27: Show the individual age
    Benji, Apr 21st, 2019
"""

import os
import unittest
from gedcom_ajry import Gedcom

class test_us27(unittest.TestCase):
    """ Test cases for US27"""

    def test_age_of_the_dead(self):
        """test the age of people who have passed away"""
        expected = [
            ('@I1@', 'Jeff Shankins', 89),
            ('@I2@', 'Bancy Pitries', 75),
            ('@I3@', 'Killy Shankins', 24)
            ]
        self.assertEqual(Gedcom('GEDCOM_files/us27/us27_age_of_the_dead.ged').us27_include_individuals_age(debug=True), expected)

    def test_age_of_the_living(self):
        """test the age of people who are alive"""
        expected = [
            ('@I1@', 'Jeff Shankins', 51),
            ('@I2@', 'Bancy Pitries', 44),
            ('@I3@', 'Killy Shankins', 22)
            ]
        self.assertEqual(Gedcom('GEDCOM_files/us27/us27_age_of_the_living.ged').us27_include_individuals_age(debug=True), expected)

if __name__ == '__main__':
    unittest.main(exit=False, verbosity=2)
