import unittest
from datetime import datetime
from gedcom_ajry import Gedcom

gdm1 = Gedcom("./GEDCOM_files/test1_us03us05_john.ged")
gdm2 = Gedcom("./GEDCOM_files/test2_us03us05_john.ged")
gdm3 = Gedcom("./GEDCOM_files/test3_us03us05_john.ged")
gdm4 = Gedcom("./GEDCOM_files/test4_us03us05_john.ged")
res1 = ['Error, death date before birth date for individual with id : @I7@']
res2 = ['Error, death date before birth date for individual with id : @I2@']
res3 = ['Error, death date before birth date for individual with id : @I15@']
res4 = []
gdm1.pretty_print()
gdm2.pretty_print()
gdm3.pretty_print()
gdm4.pretty_print()
class Sprint1us03_john(unittest.TestCase):
   def test_us05_marriage_before_death(self):
        self.assertCountEqual(gdm1.us03_birth_before_death(),res1)
        self.assertCountEqual(gdm2.us03_birth_before_death(),res2)
        self.assertCountEqual(gdm3.us03_birth_before_death(),res3)
        self.assertCountEqual(gdm4.us03_birth_before_death(),res4)

if __name__ == "__main__":
    unittest.main()
