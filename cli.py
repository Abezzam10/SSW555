""" Command Line Interface for gedcom-benji"""

import os
import click
from gedcom_ajry import Gedcom
from gedcom_ajry import MongoDB

@click.group()
def gedcom():
    """ Command line interface for SSW 555 GEDCOM file analyzer"""

@gedcom.command()
@click.argument('gedfile')
def detect(gedfile):
    """Pretty print the individuals and family tables and detect errors and anomalies of the given file"""
    ged = Gedcom(gedfile)
    mongo_instance = MongoDB()
    # mongo_instance.delete_database()
    mongo_instance.drop_collection("family")
    mongo_instance.drop_collection("individual")
    ged.pretty_print()
    ged.insert_to_mongo()

    ged.us01_date_validate()
    ged.us02_birth_before_marriage()
    ged.us03_birth_before_death()
    ged.us04_marr_b4_div()
    ged.us05_marriage_before_death()
    ged.us06_divorce_before_death()
    ged.us07_less_than_150_yrs()
    ged.us08_birt_b4_marr_of_par()
    ged.us11_no_bigamy()
    ged.us13_sibling_spacing()
    ged.us14_multi_birt_less_than_5()
    ged.us16_male_last_name()
    ged.us17_no_marriages_to_children()
    ged.us18_siblings_should_not_marry()
    ged.us19_first_cousins_should_not_marry()
    ged.us20_aunts_and_uncle()
    ged.us21_correct_gender_for_role()
    ged.us22_unique_ids()
    ged.us23_unique_name_and_birt()
    ged.us26_corrspnding_entries()

    ged.msg_print()

@gedcom.command()
@click.argument('gedfile')
def us28(gedfile):
    """US28: Order Siblings by age"""
    Gedcom(gedfile).us28_order_siblings_by_age()

@gedcom.command()
@click.argument('gedfile')
def us29(gedfile):
    """US29: List deceased people"""
    Gedcom(gedfile).us29_list_deceased()

@gedcom.command()
@click.argument('gedfile')
def us31(gedfile):
    """US31: List living single"""
    Gedcom(gedfile).us31_list_living_single()

@gedcom.command()
@click.argument('gedfile')
def us33(gedfile):
    """US33: List orphan"""
    Gedcom(gedfile).us33_list_orphans()
    
@gedcom.command()
@click.argument('gedfile')
def us32(gedfile):
    """US32: List multiple births"""
    Gedcom(gedfile).us32_list_multiple_births()

@gedcom.command()
@click.argument('gedfile')
def us34(gedfile):
    """US34: List large age differences"""
    Gedcom(gedfile).us34_list_large_age_gap()

@gedcom.command()
@click.argument('gedfile')
def us35(gedfile):
    """US35: List recent births"""
    Gedcom(gedfile).us35_list_recent_births()

@gedcom.command()
@click.argument('gedfile')
def us36(gedfile):
    """US36: List recent deaths"""
    Gedcom(gedfile).us36_list_recent_deaths()

@gedcom.command()
@click.argument('gedfile')
def us37(gedfile):
    """US37: List recent survivors"""
    Gedcom(gedfile).us37_list_recent_survivors()

@gedcom.command()
@click.argument('gedfile')
def us39(gedfile):
    """US39: List upcoming anniversaries"""
    Gedcom(gedfile).us39_list_anniversaries()

@gedcom.command()
@click.argument('gedfile')
def us27(gedfile):
    """US27: Individual age"""
    Gedcom(gedfile).us27_include_individuals_age()
