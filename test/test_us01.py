import unittest
from datetime import datetime
from gedcom_ajry import Gedcom

class test_us01(unittest.TestCase):
    """ Test cases for US01 """
    def setUp(self):
        self.current_date = datetime.now()
        self.gdm = Gedcom("./GEDCOM_files/us01/us01_dates_before_current_date.ged")
        self.indis = self.gdm.indis
        self.fams = self.gdm.fams

    def test_date_exist(self):
        # for individuals' date
        for uid, indi in self.indis.items():
            if indi.birt_dt != None and indi.deat_dt != None:
                self.assertTrue(indi.birt_dt)
                self.assertTrue(indi.deat_dt)

        # for families' date
        for uid, fam in self.fams.items():
            if fam.marr_dt != None and fam.div_dt != None:
                self.assertTrue(fam.marr_dt)
                self.assertTrue(fam.div_dt)

    def test_birth_date_before_current_date(self):
        for uid, indi in self.indis.items():
            if indi.birt_dt != None:
                self.assertTrue(indi.birt_dt < self.current_date)

    def test_death_date_before_current_date(self):
        for uid, indi in self.indis.items():
            if indi.deat_dt != None:
                self.assertTrue(indi.deat_dt < self.current_date)

    def test_marriage_date_before_current_date(self):
        for uid, fam in self.fams.items():
            if fam.marr_dt != None:
                self.assertTrue(fam.marr_dt < self.current_date)

    def test_divorce_date_before_current_date(self):
        for uid, fam in self.fams.items():
            if fam.div_dt != None:
                self.assertTrue(fam.div_dt < self.current_date)

if __name__ == "__main__":
    unittest.main(exit=False, verbosity=2)
