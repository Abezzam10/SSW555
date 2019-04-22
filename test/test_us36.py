""" US36: List Recent Deaths
    Javer, Apr 17, 2019
"""

import os
import unittest
from gedcom_ajry import Gedcom

class test_us36(unittest.TestCase):
    """ Test cases for US36"""

    def test_list_recent_death_within_30_days(self):
        expected = [['@I77@', '2019-04-07'], ['@I78@', '2019-04-15']]
        result = Gedcom('./GEDCOM_files/us36/us36_list_recent_death_within_30_days.ged').us36_list_recent_deaths(debug=True)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main(exit=False, verbosity=2)
