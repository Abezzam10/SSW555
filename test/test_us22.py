import unittest
from gedcom_ajry import Gedcom

class test_us22(unittest.TestCase):
    """ Test cases for US22 """
        
    def test_unique_ids(self):
        gdm = Gedcom("./GEDCOM_files/us22/us22_unique_id.ged")
        self.assertEqual(gdm.us22_unique_ids(debug=True), [])

    def test_duplicate_ids(self):
        gdm = Gedcom("./GEDCOM_files/us22/us22_duplicate_id.ged")
        self.assertEqual(gdm.us22_unique_ids(debug=True), [('@I1@', 'INDI')])

if __name__ == "__main__":
    unittest.main(exit=False, verbosity=2)
