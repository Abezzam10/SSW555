""" US14: multi_birt_less_than_5 
    Javer, Mar 3, 2019
    No more than five siblings should be born at the same time within a family
"""
import unittest
from gedcom_ajry import Gedcom

class test_us14(unittest.TestCase):
    """ Test cases for US14"""

    def test_multi_birt_less_than_5(self):
        """ No more than five siblings should be born at the same time within a family """
        ged = Gedcom('./GEDCOM_files/integrated_no_err.ged')
        self.assertEqual(ged.us14_multi_birt_less_than_5(debug=True), [])

if __name__ == '__main__':
    unittest.main(exit=False, verbosity=2)
    
