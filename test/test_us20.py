""" US20: Uncles and Aunt
    Benji, Feb 24th, 2019
    Aunts and uncles should not marry their nieces or nephews
"""

import unittest
from gedcom_ajry import Gedcom

class test_us20(unittest.TestCase):
    """ Test cases for US20"""

    def test_nephew_marr_aunt(self):
        """ test case nephew marries with his aunt"""
        expected = [
            (
                '@I4@', {'first': 'Ably', 'last': 'Pedersen'},
                '@I10@', {'first': 'Cam', 'last': 'Pedersen'},
                '@I7@', {'first': 'Karla', 'last': 'Pedersen'}
            )
        ]
        ged = Gedcom('./GEDCOM_files/us20_nephew_marr_aunt.ged')
        self.assertEqual(ged.us20_aunts_and_uncle(debug=True), expected)

    def test_niece_marr_uncle(self):
        """ test case niece marries with her uncle"""
        expected = [
            (
                '@I4@', {'first': 'Ably', 'last': 'Pedersen'},
                '@I11@', {'first': 'Molly', 'last': 'Pedersen'},
                '@I6@', {'first': 'Gisilbert', 'last': 'Pedersen'}
            )
        ] 
        ged = Gedcom('./GEDCOM_files/us20_niece_marr_uncle.ged')
        self.assertEqual(ged.us20_aunts_and_uncle(debug=True), expected)
    
    def test_no_err(self):
        """ test case no error"""
        ged = Gedcom('./GEDCOM_files/us20_no_err.ged')
        self.assertEqual(ged.us20_aunts_and_uncle(debug=True), [])

if __name__ == '__main__':
    unittest.main(exit=False, verbosity=2)
