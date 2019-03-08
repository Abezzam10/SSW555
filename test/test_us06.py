""" US06: Divorce before death 
    Benji, Feb 21st, 2019
    Divorce can only occur before death of both spouses
"""

import unittest
from gedcom_ajry import Gedcom

class test_us06(unittest.TestCase):
    """ Test cases for US06"""

    def test_both_die_before_divorce(self):
        """ husband and wife both die before divorce"""
        expected = [
            ('Jack Monroe', 'husband', '@F1@', '05/16/97', '02/10/04'),
            ('Lucy Oliver', 'wife', '@F1@', '03/02/03', '02/10/04')
            ]
        ged = Gedcom('./GEDCOM_files/us06/us06_both_die_b4_div.ged')
        self.assertEqual(ged.us06_divorce_before_death(debug=True), expected)
        
    def test_both_live_divorce(self):
        """ husband and wife divorce but both are alive"""
        ged = Gedcom('./GEDCOM_files/us06/us06_both_live_div.ged')
        self.assertEqual(ged.us06_divorce_before_death(debug=True), [])

    def test_both_live_not_divorce(self):
        """ husband and wife are alive and happy ever after"""
        ged = Gedcom('./GEDCOM_files/us06/us06_both_live_not_div.ged')
        self.assertEqual(ged.us06_divorce_before_death(debug=True), [])

    def test_husb_die_after_divorce(self):
        """ husband dies after divorce"""
        ged = Gedcom('./GEDCOM_files/us06/us06_husb_die_af_div.ged')
        self.assertEqual(ged.us06_divorce_before_death(debug=True), [])

    def test_husb_die_before_divorce(self):
        """ husband dies before divorce"""
        ged = Gedcom('./GEDCOM_files/us06/us06_husb_die_b4_div.ged')
        expected = [('Jack Monroe', 'husband', '@F1@', '05/16/97', '02/10/04')]
        self.assertEqual(ged.us06_divorce_before_death(debug=True), expected)

if __name__ == '__main__':
    unittest.main(exit=False, verbosity=2)
    
