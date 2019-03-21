import unittest
from datetime import datetime
from gedcom_ajry import Gedcom
                                                                # birthdays of siblings
gdm1 = Gedcom("./GEDCOM_files/us13/us13_within9months.ged")     # 24 AUG 1997 and 22 NOV 1997
gdm2 = Gedcom("./GEDCOM_files/us13/us13_within2days.ged")       # 24 AUG 1997 and 26 AUG 1997
gdm3 = Gedcom("./GEDCOM_files/us13/us13_within1day.ged")        # 24 AUG 1997 and 25 AUG 1997
gdm4 = Gedcom("./GEDCOM_files/us13/us13_properbirthdays.ged")   # 24 AUG 1997 and 22 APR 1993

class Sprint2us13_john(unittest.TestCase):
    def test_us13_within9months(self):
        res1 = [('Jordon Mccarthy','@I4@','Harold Mccarthy','@I1@',90)]
        i=-1
        for tupl in gdm1.us13_sibling_spacing(debug=True):
            i=i+1
            self.assertCountEqual(tuple(tupl),tuple(res1[i]))
    
    def test_us13_within2days(self):
        res2 = [('Jordon Mccarthy','@I4@','Harold Mccarthy','@I1@',2)]
        i=-1
        for tupl in gdm2.us13_sibling_spacing(debug=True):
            i=i+1
            self.assertCountEqual(tuple(tupl),tuple(res2[i]))
    
    def test_us13_within1day(self):
        res3=[]
        i=-1
        for tupl in gdm3.us13_sibling_spacing(debug=True):
            i=i+1
            self.assertCountEqual(tuple(tupl),tuple(res3[i]))

    def test_us13_properbirthdays(self):
        res4=[]
        i=-1
        for tupl in gdm4.us13_sibling_spacing(debug=True):
            i=i+1
            self.assertCountEqual(tuple(tupl),tuple(res4[i]))


if __name__ == "__main__":
    unittest.main()