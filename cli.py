""" Command Line Interface for gedcom-benji"""

import os
import click
from gedcom_benji import Gedcom

@click.command()
@click.argument('gedfile')
def gedcom(gedfile):
    Gedcom(gedfile)
    