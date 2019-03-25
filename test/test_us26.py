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
        ged = Gedcom('GEDCOM_files/us26/us26_indi_entry_bleach.ged')
        ged.insert_to_mongo()

        expected = [('Individuals', '@I4@', 'family collection')]
        res = ged.us26_corrspnding_entries(debug=True)

        self.assertEqual(expected, res)

        MONGO.drop_collection('family')
        MONGO.drop_collection('individual')

    def test_no_err(self):
        """ Positive test for US26."""
        ged = Gedcom('GEDCOM_files/us26/us26_no_err.ged')
        ged.insert_to_mongo()

        expected = []
        res = ged.us26_corrspnding_entries(debug=True)

        self.assertEqual(expected, res)

        MONGO.drop_collection('family')
        MONGO.drop_collection('individual')

if __name__ == '__main__':
    unittest.main(exit=False, verbosity=2)
