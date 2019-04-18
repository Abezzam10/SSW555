""" John, 18th April 2019
    US34 : List all couples who were married when the older spouse was more than twice as old as the younger spouse
"""
import unittest
from datetime import datetime
from gedcom_ajry import Gedcom

gdm1 = Gedcom("./GEDCOM_files/us34/us34_twocouples.ged")
gdm2 = Gedcom("./GEDCOM_files/us34/us34_nocouples.ged")

class test_us34(unittest.TestCase):
    def test_twoCouplesWithLargeAgeGap(self):
        result = [('@F17@','@I74@','Sprfor Sobo','@I40@','Tinatin Benjamin'), ('@F32@','@I15@','Morgan McClean','@I47@','Moiss McClean')]
        i=-1
        for tupl in gdm1.us34_list_large_age_gap(debug=True):
            i=i+1
            self.assertCountEqual(tuple(tupl),tuple(result[i]))

    def test_noCouplesWithLargeAgeGap(self):
        result = []
        i=-1
        for tupl in gdm2.us34_list_large_age_gap(debug=True):
            i=i+1
            self.assertCountEqual(tuple(tupl),tuple(result[i]))

if __name__ == "__main__":
    unittest.main()