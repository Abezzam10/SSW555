import unittest
from datetime import datetime
from gedcom_ajry import Gedcom

gdm1 = Gedcom("./GEDCOM_files/us05/test1_us05_john.ged")
gdm2 = Gedcom("./GEDCOM_files/us05/test2_us05_john.ged")
gdm3 = Gedcom("./GEDCOM_files/us05/test3_us05_john.ged")
gdm4 = Gedcom("./GEDCOM_files/us05/test4_us05_john.ged")
res1 = [('wife','Lilia Orourke','@I7@','@F2@')]
res2 = [('husband','Oswaldo Mccarthy','@I2@','@F1@')]
res3 = [('husband','Winfred Ault','@I15@','@F3@')]

class Sprint1us03_john(unittest.TestCase):
    def test_us05_marriage_before_death(self):
        self.assertCountEqual(gdm1.us05_marriage_before_death(debug=True),res1)
        self.assertCountEqual(gdm2.us05_marriage_before_death(debug=True),res2)
        self.assertCountEqual(gdm3.us05_marriage_before_death(debug=True),res3)
        self.assertCountEqual(gdm4.us05_marriage_before_death(debug=True),[])

if __name__ == "__main__":
    unittest.main()
