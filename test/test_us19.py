""" John, 7th April 2019
    US19 : First cousins should not marry one another
"""
import unittest
from datetime import datetime
from gedcom_ajry import Gedcom

gdm1 = Gedcom("./GEDCOM_files/us19/us19_first_cousins_married.ged")
gdm2 = Gedcom("./GEDCOM_files/us19/us19_first_cousins_not_married.ged")

class test_us19(unittest.TestCase):
    def test_first_cousins_married(self):
        result = [('Andre Benjamin','@I18@','Jasmine Colman','@I25@'), ('Jasmine Colman','@I25@','Andre Benjamin','@I18@')]
        i=-1
        for tupl in gdm1.us19_first_cousins_should_not_marry(debug=True):
            i=i+1
            self.assertCountEqual(tuple(tupl),tuple(result[i]))

    def test_first_cousins_not_married(self):
        result = []
        i=-1
        for tupl in gdm2.us19_first_cousins_should_not_marry(debug=True):
            i=i+1
            self.assertCountEqual(tuple(tupl),tuple(result[i]))

if __name__ == "__main__":
    unittest.main()