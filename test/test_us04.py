import unittest
from datetime import datetime
from gedcom_ajry import Gedcom
                                                                        # Marriage and divorce dates
gdm1 = Gedcom("./GEDCOM_files/us04/us04_divorcebeforemarriage.ged")     # 8 OCT 1980 and 6 SEP 1979
gdm2 = Gedcom("./GEDCOM_files/us04/us04_divorcemarriagesamedate.ged")   # 8 OCT 1980 and 8 OCT 1980
gdm3 = Gedcom("./GEDCOM_files/us04/us04_properdivorcemarriage.ged")     # 8 OCT 1980 and 6 SEP 1993

class Sprint2us13_john(unittest.TestCase):
    def test_divorceb4marriage(self):
        res1 = [('@F3@')]
        self.assertCountEqual(gdm1.us04_marr_b4_div(debug=True),res1)
    
    def test_divorcemarriagesamedate(self):
        res2 = []
        self.assertCountEqual(gdm2.us04_marr_b4_div(debug=True),res2)
    
    def test_properdivorcemarriage(self):
        res3 = []
        self.assertCountEqual(gdm3.us04_marr_b4_div(debug=True),res3)
        
if __name__ == "__main__":
    unittest.main()