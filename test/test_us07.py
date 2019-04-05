""" US07: Less than 150 years old
    Benji, Feb 24th, 2019
    Death should be less than 150 years after birth for dead people, and
    current date should be less than 150 years after birth for all living people
"""

import os
import unittest
from gedcom_ajry import Gedcom

class test_us07(unittest.TestCase):
    """ Test cases for US07"""

    def test_over_150yr_alive(self):
        """ Test the person is over 150 years old and alive."""
        expected = [('@I1@', 'Frank Davis', 219)]
        res = Gedcom('GEDCOM_files/us07/us07_over_150yr_alive.ged').us07_less_than_150_yrs(debug=True)
        self.assertEqual(res, expected)

    def test_over_150yr_dead(self):
        """ Test the person is over 150 years old and dead."""
        expected = [('@I1@', 'Frank Davis', 152)]
        res = Gedcom('GEDCOM_files/us07/us07_over_150yr_dead.ged').us07_less_than_150_yrs(debug=True)
        self.assertEqual(res, expected)

    def test_less_than_150yr_alive(self):
        """ Test the person is less than 150 year old and alive."""
        expected = []
        res = Gedcom('GEDCOM_files/us07/us07_less_than_150yr_alive.ged').us07_less_than_150_yrs(debug=True)
 
        self.assertEqual(res, expected)

    def test_less_than_150yr_dead(self):
        """ Test the person is less than 150 year old and alive."""
        expected = []
        res = Gedcom('GEDCOM_files/us07/us07_less_than_150yr_dead.ged').us07_less_than_150_yrs(debug=True)
 
        self.assertEqual(res, expected)

if __name__ == '__main__':
    unittest.main(exit=False, verbosity=2)
