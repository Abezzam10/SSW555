import unittest
from datetime import datetime
from gedcom_ajry import Gedcom

gdm1 = Gedcom("./GEDCOM_files/us05/test1_us05_john.ged")
gdm2 = Gedcom("./GEDCOM_files/us05/test2_us05_john.ged")
gdm3 = Gedcom("./GEDCOM_files/us05/test3_us05_john.ged")
gdm4 = Gedcom("./GEDCOM_files/us05/test4_us05_john.ged")
res1 = ['Error, death before her marriage of wife with id : @I7@']
res2 = ['Error, death before marriage of husband with id : @I2@']
res3 = ['Error, death before marriage of husband with id : @I15@']
res4 = []
class Sprint1us03_john(unittest.TestCase):
    def test_us05_marriage_before_death(self):
        self.assertCountEqual(gdm1.us05_marriage_before_death(),res1)
        self.assertCountEqual(gdm2.us05_marriage_before_death(),res2)
        self.assertCountEqual(gdm3.us05_marriage_before_death(),res3)
        self.assertCountEqual(gdm4.us05_marriage_before_death(),res4)

if __name__ == "__main__":
    unittest.main()
