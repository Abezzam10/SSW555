import unittest
from gedcom_ajry import Gedcom

class test_us22(unittest.TestCase):
    """ Test cases for US22 """
        
    def test_unique_ids(self):
        gdm = Gedcom("./GEDCOM_files/us01/proj01.ged")
        self.assertEqual(gdm.us22_unique_ids(debug=True), [])

if __name__ == "__main__":
    unittest.main(exit=False, verbosity=2)
