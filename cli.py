""" Command Line Interface for gedcom-benji"""

import os
import click
from gedcom_ajry import Gedcom
from gedcom_ajry import MongoDB

@click.command()
@click.argument('gedfile')
def gedcom(gedfile):
    ged = Gedcom(gedfile)
    mongo_instance = MongoDB()
    # mongo_instance.delete_database()
    mongo_instance.drop_collection("family")
    mongo_instance.drop_collection("individual")
    ged.insert_to_mongo()
    ged.pretty_print()
    ged.us01_date_validate()
    ged.us02_birth_before_marriage()
    ged.us03_birth_before_death()
    ged.us05_marriage_before_death()
    ged.us06_divorce_before_death()
    ged.us11_no_bigamy()
    ged.us20_aunts_and_uncle()
    ged.us22_unique_ids()

    ged.us14_multi_birt_less_than_5()
    ged.us16_male_last_name()

    ged.us07_less_than_150_yrs()
    ged.us26_corrspnding_entries()

    ged.us04_marr_b4_div()
    ged.us08_birt_b4_marr_of_par()
    ged.us13_sibling_spacing()
    ged.us23_unique_name_and_birt()

    ged.msg_print()
