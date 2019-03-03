""" US16: male_last_name
    Javer, Mar 3, 2019
    To check each male has the last name within each family
"""
import unittest
from gedcom_ajry import Gedcom

class test_us16(unittest.TestCase):
    """ Test cases for US16"""

    def test_male_same_last_name_in_family(self):
        """ male last names should be same in a family"""
        ged = Gedcom('./GEDCOM_files/integrated_no_err.ged')
        self.assertEqual(ged.us16_male_last_name(debug=True), [])

if __name__ == '__main__':
    unittest.main(exit=False, verbosity=2)
    
