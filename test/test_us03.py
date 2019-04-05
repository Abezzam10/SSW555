import unittest
from datetime import datetime
from gedcom_ajry import Gedcom

gdm1 = Gedcom("./GEDCOM_files/us03/test1_us03_john.ged")
gdm2 = Gedcom("./GEDCOM_files/us03/test2_us03_john.ged")
gdm3 = Gedcom("./GEDCOM_files/us03/test3_us03_john.ged")
gdm4 = Gedcom("./GEDCOM_files/us03/test4_us03_john.ged")
res1 = [('Lilia Orourke','@I7@')]
res2 = [('Oswaldo Mccarthy','@I2@')]
res3 = [('Winfred Ault','@I15@')]

class Sprint1us03_john(unittest.TestCase):
   def test_us05_marriage_before_death(self):
        self.assertEqual(gdm1.us03_birth_before_death(debug=True),res1)
        self.assertEqual(gdm2.us03_birth_before_death(debug=True),res2)
        self.assertEqual(gdm3.us03_birth_before_death(debug=True),res3)
        self.assertEqual(gdm4.us03_birth_before_death(debug=True),[])

if __name__ == "__main__":
    unittest.main()
