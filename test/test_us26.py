""" US26: Less than 150 years old
    Benji, Feb 24th, 2019
    Death should be less than 150 years after birth for dead people, and
    current date should be less than 150 years after birth for all living people
"""

import os
import unittest
from gedcom_ajry import Gedcom
from mongo_db import MongoDB

MONGO = MongoDB()

class test_us26(unittest.TestCase):
    """ Test cases for US26"""

    def test_indi_entry_bleach(self):
        """ Individual data missed in family collection."""
        self.assertEqual(
            Gedcom('GEDCOM_files/us26/us26_indi_entry_bleach.ged').us26_corrspnding_entries(debug=True),
            [('Individual', '@I4@')]
            )

    def test_no_err(self):
        """ Positive test for US26."""
        self.assertEqual(
            Gedcom('GEDCOM_files/us26/us26_no_err.ged').us26_corrspnding_entries(debug=True),
            []
            )

if __name__ == '__main__':
    unittest.main(exit=False, verbosity=2)
