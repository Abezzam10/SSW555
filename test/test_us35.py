""" US35: List Recent Births
    Javer, Apr 17, 2019
"""

import os
import unittest
from gedcom_ajry import Gedcom

class test_us35(unittest.TestCase):
    """ Test cases for US35"""

    def test_list_recent_birth_within_30_days(self):
        expected = [['@I81@', '2019-04-14']]
        result = Gedcom('./GEDCOM_files/us35/us35_list_recent_birth_within_30_days.ged').us35_list_recent_births(debug=True)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main(exit=False, verbosity=2)
