""" GEDCOM error distinguish"""

import os
from datetime import datetime




class Gedcom:
    """ a class used to read the given GEDCOM file and build the database based on it
        and look for errors and anomalies.
    """

    level_tags = {
        '0': {'INDI': 2, 'FAM': 2, 'HEAD': 1, 'TRLR': 1, 'NOTE': 1},
        '1': {'NAME': 1, 'SEX': 1, 'BIRT': 1, 'DEAT': 1, 'FAMC': 1, 'FAMS': 1, \
                'MARR': 1, 'HUSB': 1, 'WIFE': 1, 'CHIL': 1, 'DIV': 1},
        '2': {'DATE': 1}
    }  # Identify the tags by level_number

    dt_fmt = '%d %b %Y'  # datetime format of DATE
    sexes = ('M', 'F')  # data of sex
    names_regex = r'^([\w]+) /([\w]+)/$'  # for extract the first name and last name without str.split()

    def __init__(self, path):
        self.path = path
        self.path_validate()
        self.data_parser()

    def path_validate(self):
        """ If a invalid path is given, raise an OSError"""
        if not os.path.isfile(os.path.abspath(self.path)):
            raise OSError(f'Error: {self.path} is not a valid path!')
    
    def data_parser(self):
        """ open the file from given path and print the analysis of data"""
        try:
            fp = open(self.path, encoding='utf-8')
        except FileNotFoundError:
            raise FileNotFoundError(f'Error: can\'t read data file {self.path}.')
        else:
            with fp:
                for line in fp:
                    self.line_processor(line.strip())

    def line_processor(self, line: str):
        """ process each line read from the file
            the formats of line are:
            - level in ('1', '2'):
                    <level> <tag> <argument>
            - level == '0':
                    <level> <id> <tag>  for tag in ('INDI', 'FAM')
                    <level> <tag> [<argument>]  for tag in ('NOTE', 'HEAD', 'TRLR')
        """
        print(f'--> {line}')

        fields = line.split(' ', 2)
        level = fields[0]

        if level in Gedcom.level_tags:
            res, tail = [level], list()

            for ind, item in enumerate(fields[1: ], start=1):
                if item in Gedcom.level_tags[level] and ind == Gedcom.level_tags[level][item]:  # valid tag in valid position
                    res.extend([item, 'Y'])
                elif item in Gedcom.level_tags[level] and ind != Gedcom.level_tags[level][item]: # valid tag in invalid poition
                    res.extend([item, 'N'])
                else:
                    tail.append(item)

            if len(res) == 1:  # no tag found
                res.extend(tail)
                res.insert(2, 'N')
            elif tail:
                res.extend(tail)

        else:  # It doesn't exist
            res = fields
            res.insert(2, 'N')

        print('<-- ' + '|'.join(res))




def main():
    """ Entrance"""
    gdm = Gedcom('/Users/benjamin/Documents/Python_Scripts/SSW555/sample_data.ged')

if __name__ == "__main__":
    main()
        