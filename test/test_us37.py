""" John, April 18th 2019
    US37 : List all living spouses and descendants of people in a GEDCOM file who died in the last 30 days
"""
import unittest
from datetime import datetime
from gedcom_ajry import Gedcom

gdm1 = Gedcom("./GEDCOM_files/us37/us37_onedeath.ged")
gdm2 = Gedcom("./GEDCOM_files/us37/us37_nodeath.ged")


class test_us37(unittest.TestCase):
    def test_one_death(self):
        result = {
            '@F27@' : {
                'death' : [('@I78@','Unfotant Bumm','2019-04-15')],
                'survivorList' : {
                    'spouse' : {('@I69@','Luckinbet Beynocne')},
                    'children' : {('@I79@','Givbrth Bumm')}
                }   
            }
        }
        self.assertDictEqual(gdm1.us37_list_recent_survivors(debug=True),result)
    
    def test_no_deaths(self):
        result = {}
        self.assertDictEqual(gdm2.us37_list_recent_survivors(debug=True),result)

    
if __name__ == "__main__":
    unittest.main()