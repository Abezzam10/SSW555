""" Ray, Feb 22th, 2019
    US11: No bigamy
    Married person should not be in another marriage
"""

import unittest
from gedcom_ajry import Gedcom

class test_us11(unittest.TestCase):
    """ Test cases for US11"""

    def test_no_bigamy(self):
        """ None of the spouses are involved in multiple marriages"""
        ged = Gedcom('./GEDCOM_files/us11/test04.ged')
        self.assertEqual(ged.us11_no_bigamy(debug=True), [])

    def test_prev_marr_end_with_div(self):
        """ Previous marriage ends with divorce"""
        ged = Gedcom('./GEDCOM_files/us11/us11_prev_div.ged')
        expected = [
            ('@I1@', 'Fake Arshel', '@F1@ and @F2@')
        ]
        self.assertEqual(ged.us11_no_bigamy(debug=True), expected)

    def test_prev_marr_end_indi_dies(self):
        """ Previous marriage ends with the current person's death"""
        ged = Gedcom('./GEDCOM_files/us11/us11_prev_indi_dies.ged')
        expected = [
            ('@I1@', 'Fake Arshel', '@F1@ and @F2@')
        ]
        self.assertEqual(ged.us11_no_bigamy(debug=True), expected)

    def test_prev_marr_end_partner_dies(self):
        """ Previous marriage ends with the partner's death"""
        ged = Gedcom('./GEDCOM_files/us11/us11_prev_partner_dies.ged')
        expected = [
            ('@I1@', 'Fake Arshel', '@F1@ and @F2@')
        ]
        self.assertEqual(ged.us11_no_bigamy(debug=True), expected)

if __name__ == '__main__':
    unittest.main(exit=False, verbosity=2)
    
