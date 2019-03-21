import unittest
from datetime import datetime
from gedcom_ajry import Gedcom

gdm1 = Gedcom("./GEDCOM_files/us13/us13_within9months.ged")

res1 = [('Jordon Mccarthy','@I4@','Harold Mccarthy','@I1@',90)]


class Sprint2us13_john(unittest.TestCase):
    def test_us13_sibling_spacing(self):
        i=-1
        for tupl in gdm1.us13_sibling_spacing(debug=True):
            i=i+1
            self.assertCountEqual(tuple(tupl),tuple(res1[i]))

if __name__ == "__main__":
    unittest.main()