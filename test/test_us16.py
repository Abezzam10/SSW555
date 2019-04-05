""" US16: male_last_name
    Javer, Mar 3, 2019
    To check each male has the last name within each family
"""
import unittest
from gedcom_ajry import Gedcom
from mongo_db import MongoDB

class test_us16(unittest.TestCase):
    """ Test cases for US16"""

    def test_same_lastname(self):
        """ Positive test, males' last names are the same"""
        mongo_instance = MongoDB()
        mongo_instance.drop_collection("family")
        mongo_instance.drop_collection("individual")

        ged = Gedcom('./GEDCOM_files/us16/us16_male_last_name_same.ged')
        ged.insert_to_mongo()
        
        self.assertEqual(
            ged.us16_male_last_name(debug=True),
            []
        )

    def test_diff_lastname(self):
        """ Negative test, males' last names are different"""
        mongo_instance = MongoDB()
        mongo_instance.drop_collection("family")
        mongo_instance.drop_collection("individual")

        ged = Gedcom('./GEDCOM_files/us16/us16_male_last_name_diff.ged')
        ged.insert_to_mongo()

        self.assertEqual(
            ged.us16_male_last_name(debug=True),
            [('@F1@', '@I2@, @I3@', 'LastName,Test')]
        )

if __name__ == '__main__':
    unittest.main(exit=False, verbosity=2)
    
