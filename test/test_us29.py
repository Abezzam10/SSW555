""" John, 7th April 2019
    US29 : List all deceased individuals in a GEDCOM file
"""
import unittest
from datetime import datetime
from gedcom_ajry import Gedcom

gdm1 = Gedcom("./GEDCOM_files/us29/us29_some_deaths.ged")
gdm2 = Gedcom("./GEDCOM_files/us29/us29_no_deaths.ged")
gdm3 = Gedcom("./GEDCOM_files/us29/us29_one_death.ged")

class test_us29(unittest.TestCase):
    def test_some_deaths(self):
        result = {
            '@I7@' : 'Lilia Orourke',
            '@I12@' : 'Minna Jensen',
            '@I15@' : 'Winfred Ault',
            '@I21@' : 'Vivian Sue'
        }
        self.assertDictEqual(gdm1.us29_list_deceased(debug=True),result)
    
    def test_no_deaths(self):
        result = {}
        self.assertDictEqual(gdm2.us29_list_deceased(debug=True),result)

    def test_one_death(self):
        result = {
            '@I13@' : 'Mellisa Triplett'
        }
        self.assertDictEqual(gdm3.us29_list_deceased(debug=True),result)

if __name__ == "__main__":
    unittest.main()