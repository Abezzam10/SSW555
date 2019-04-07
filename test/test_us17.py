""" US17: No marriage to children
    Benji, Feb 21st, 2019
    Parents should not marry to children
"""

import unittest
from gedcom_ajry import Gedcom

class test_us17(unittest.TestCase):
    """ Test cases for US17"""

    def test_no_error(self):
        """Nothing wrong happen here"""
        path = './GEDCOM_files/us17/us17_no_error.ged'
        self.assertEqual(Gedcom(path).us17_no_marriages_to_children(debug=True), [])

    def test_marriage_with_own_children(self):
        """Somebody does marry to the child of their own, eww"""
        path = './GEDCOM_files/us17/us17_marry_with_child.ged'
        self.assertEqual(
            Gedcom(path).us17_no_marriages_to_children(debug=True),
            [('@I1@', '@I5@', '@F3@')]
        )

if __name__ == '__main__':
    unittest.main(exit=False, verbosity=2)
    
