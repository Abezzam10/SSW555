""" GEDCOM error distinguish"""

import os
import re
import json
import pymongo
from subprocess import Popen, PIPE
from pymongo import MongoClient
from tabulate import tabulate
from datetime import datetime
from collections import defaultdict


class ShellxMongo:
    """ A class that wrap the shell commands needed for establish the mongo deamon silently
        and kill the process gracefully 
    """

    HOME = os.path.expanduser('~')
    PORT = '27018'

    @property
    def dbpath(self):
        """ create directory ~/data/db if not exists"""
        dbpath = os.path.join(ShellxMongo.HOME, 'data', 'db')
        if not os.path.isdir(dbpath):  # ~/data/db not exist
            os.makedirs(dbpath)
        return dbpath

    def run_mongod(self):
        """ set up the MongoDB instance, but silently
            also get the backgroud pid of mongod 
        """
        process = Popen(f'mongod --fork --syslog --port {ShellxMongo.PORT} --dbpath {self.dbpath}', shell=True, stdout=PIPE)  # create the MongoDB deamon in the background
        
        # get the process id so that after the operation we can kill the MongoDB instance
        process_msg = process.stdout.read().decode()
        pid_pattern = r'forked process: ([\d]+)'
        self.pid = re.search(pid_pattern, process_msg).group(1)

    def kill_mongo(self):
        """ kill the backgroud process of mongod"""
        Popen(f'kill {self.pid}', shell=True)
        
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
        self.raw_data = []
        self.indis = {}
        self.fams = {}
        self.path_validate()

        self.mongod = ShellxMongo()  # shell function wrapper
        self.client = None  # mongo client
        
        self.data_parser()  # processing data
        self.lst_to_obj()
        #self.pretty_print()

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
                for ln_ind, line in enumerate(fp):
                    try:
                        data = ln_ind, *self._line_processor(line.strip())
                    except ValueError as err:
                        pass  # do nothing for now
                    else:
                        self.raw_data.append(data)

    def _line_processor(self, line):
        """ process each line read from the file."""

        fields = line.split(' ', 2)  
        level = fields[0]
        res = {'level': level, 'tag': None, 'arg': None}

        if level in Gedcom.level_tags:
            tail = list()

            for ind, item in enumerate(fields[1: ], start=1):
                if item in Gedcom.level_tags[level] and ind == Gedcom.level_tags[level][item]:  # valid tag in valid position
                    res['tag'] = item
                elif item in Gedcom.level_tags[level] and ind != Gedcom.level_tags[level][item]: # valid tag in invalid poition                    
                    raise ValueError('Error: Tag not in correct position.')
                else:  # argument(s)
                    tail.append(item)
            
            if not res['tag']:  # no tag found, len(tail) == 2
                raise ValueError('Error: No tag is found.')

            elif tail:  # tag found in right position, len(tail) == 1
                res['arg'] = tail[0]

            return res['level'], res['tag'], res['arg']

        else:
            raise ValueError('Error: Invalid level_num.')

    def lst_to_obj(self):
        """ translate the raw data in the list to dict of entity objects"""
        data_iter = iter(self.raw_data)
        attr_map = {
            'INDI': {
                'INDI': 'indi_id', 'NAME': 'name', 'SEX': 'sex', 'BIRT': 'birt_dt', 'DEAT': 'deat_dt', 'FAMC': 'fam_c', 'FAMS': 'fam_s'
            },
            'FAM': {
                'FAM': 'fam_id', 'MARR': 'marr_dt', 'DIV': 'div_dt', 'HUSB': 'husb_id', 'WIFE': 'wife_id', 'CHIL': 'chil_id'
            }
        }
        cat_cont = {'INDI': self.indis, 'FAM': self.fams}
        cat_pool = {'INDI': Individual, 'FAM': Family}

        curr_entity = None
        curr_id = None
        curr_cat = None
        # curr_attr = {}

        for ln_ind, lvl, tag, arg in data_iter:

            if lvl == '0' and tag in cat_pool:  # find a new entity
                if curr_entity:  # update the current entity in data containers
                    cat_cont[curr_cat][curr_id] = curr_entity
                    curr_entity, curr_cat, curr_id = None, None, None  # *NOTE* can be deleted maybe?
                
                # when tag in ('INDI', 'FAM'), arg is the id of this entity
                curr_entity, curr_cat, curr_id = cat_pool[tag](arg), tag, arg

            if curr_entity and lvl == '1':  # in the process of constructing an entity
                attr = attr_map[curr_cat][tag]

                if tag in ('BIRT', 'DEAT', 'MARR', 'DIV'):  # the arg are None, go to next line get the arg for val
                    ln_ind, lvl, tag, arg = next(data_iter)
                    #if tag == '2' and arg == 'DATE' *NOTE* this is not needed for this project as we assume this is not grammar error
                    curr_entity[attr] = datetime.strptime(arg, Gedcom.dt_fmt)

                elif tag == 'NAME':  # use regex to extract the first name and last name, SHOW OFF PURPOSE ONLY :P
                    regex_obj = re.search(Gedcom.names_regex, arg)
                    curr_entity[attr] = f'{regex_obj.group(2)}, {regex_obj.group(1)}'  # name_fmt = r'last_name, first_name'

                elif tag == 'CHIL':  # beware that the the value of CHIL is a set
                    curr_entity[attr].add(arg)

                else:
                    curr_entity[attr] = arg

    def pretty_print(self):
        """ put everything in a fancy table
            row_fmt for INDI:
                [ID, Name, Gender, Birthday, Age, Alive, Death, Child, Spouse]
            row_fmt for FAM:
                [ID, Marr, Div, Husb_id, Husb_nm, Wife_id, Wife_nm, Chil_ids]
        """

        print('---Individuals---')
        indi_rows = list()
        for uid, indi in self.indis.items():
            indi_rows.append(indi.pp_row())
        print(tabulate(indi_rows, headers=Individual.pp_header, tablefmt='fancy_grid', showindex='never'))

        print('\n\n')

        print('---Families---')
        fams_rows = list()
        for uid, fam in self.fams.items():
            id_, marr, div, husb_id, wife_id, chil_ids = fam.pp_row()
            husb_nm, wife_nm = self.indis[husb_id].name, self.indis[wife_id].name
            fams_rows.append((id_, marr, div, husb_id, husb_nm, wife_id, wife_nm, chil_ids))  
        print(tabulate(fams_rows, headers=Family.pp_header, tablefmt='fancy_grid', showindex='never'))              

    def _build_mongo(self):
        """ invoke this method everytime at the start of the userstory
            create a mongodb and insert the data
            store the mongo client as an instance attr
            return a collection reference for use in user story method
        """
        indi_mg = [i.mongo_data() for i in self.indis.values()]  # create data set for insert_many()
        fam_mg = [f.mongo_data() for f in self.fams.values()]
        
        self.client = MongoClient('localhost', 27018)
        db = self.client['gedcom']
        
        entts = db['entity']
        entts.insert_many([*indi_mg, *fam_mg])

        return entts

    def _drop_mongo(self):
        """ invoke this method every time at the end of the use story"""
        db = self.client['gedcom']
        db.drop_collection('entity')
        self.client.close()
        self.client = None

    def us65536_example(self):
        """ this is an example for using mongodb in our progamming
            if you are using MongoDB in your implementation of the use stories, following lines of code are mandatory.
            The process for using a mongodb is
              1. Establish the MongoDB deamon, I wrap it up in ShellxMongo to make it run in the background silently.
              2. Create a connection to MongoDB using MongoClient in pymongo, the wrapper function will return a reference
                 of the collection and you can use it to do all the NoSQL operations.
              3. implement your code.
              4. After your code finishs, drop all the data(I'll specify the reason in stand up meeting)
              5. Kill the background process using ShellxMongo's method
        """
        self.mongod.run_mongod()  # Step 1: create a MongoDB instance in the background
        collection_of_all_entities = self._build_mongo()  # Step 2: create mongo client in python, insert all of the data

        # Step 3: implement your code
        # this 'collection_of_all_entities' is the reference to the collection
        # query operations are wrapped up by pymongo
        # here is an example for using this reference object
        for doc in collection_of_all_entities.find({'cat': 'fam'}):
            fam_id, marr_dt = doc['_id'], doc['marr_dt'].strftime('%d %b %Y')
            print(f'Family entity ID: {fam_id}, spouses married at {marr_dt}')  # print the id and marriage date of every family entity

        self._drop_mongo()  # Step 4: drop all of the data
        self.mongod.kill_mongo()  # Step 5: kill the process of mongod run in the background

class Entity:
    """ ABC for Individual and Family, define __getitem__ and __setitem__."""

    def __getitem__(self, attr):
        """ get the attributes values"""
        if attr in self.__dict__:
            return self.__dict__[attr]
        else:
            raise AttributeError(f'Attribute {attr} not found')

    def __setitem__(self, attr, val):
        """ update the attributes values"""
        if attr in self.__dict__:
            self.__dict__[attr] = val
        else:
            raise AttributeError(f'Attribute {attr} not found')

    def mongo_data(self):
        """ return a dictionary with mongodb data for database"""
        raise NotImplementedError('Method hasn\'t been implemented yet.')

    def pp_row(self):
        """ Return a row for command line pretty print"""
        raise NotImplementedError('Method hasn\'t been implemented yet.')

class Individual(Entity):
    """ Represent the individual entity in the GEDCOM file"""

    pp_header = ('ID', 'Name', 'Gender', 'Birthday', 'Age', 'Alive', 'Death', 'Child', 'Spouse')

    def __init__(self, indi_id):
        self.indi_id = indi_id
        self.name = ''
        self.sex = ''
        self.birt_dt = None
        self.deat_dt = None
        self.fam_c = ''
        self.fam_s = ''

    @property
    def age(self):
        """ return the age of this individual"""
        if self.birt_dt:
            age_td = datetime.today() - self.birt_dt if not self.deat_dt else self.deat_dt - self.birt_dt
            return (age_td.days + age_td.seconds // 86400) // 365
        else:
            return 'No birth date.'

    def mongo_data(self):
        """ return a dictionary with mongodb data for database"""
        return {
            '_id': self.indi_id,
            'cat': 'indi',  # only used for mongodb to distinguish entity catagory
            'name': self.name,
            'sex': self.sex,
            'birt_dt': self.birt_dt,
            'deat_dt': self.deat_dt,
            'age': self.age,
            'fam_c': self.fam_c,
            'fam_s': self.fam_s
        }

    def pp_row(self):
        """ return a data sequence:
            [ID, Name, Gender, Birthday, Age, Alive, Death, Child, Spouse]
        """
        return self.indi_id, self.name, self.sex, \
                self.birt_dt.strftime('%Y-%m-%d'), self.age, True if not self.deat_dt else False, self.deat_dt.strftime('%Y-%m-%d') if self.deat_dt else 'NA', \
                self.fam_c if self.fam_c else 'NA', self.fam_s if self.fam_s else 'NA' 

class Family(Entity):
    """ Represent the family entity in the GEDCOM file"""

    pp_header = ('ID', 'Marr', 'Div', 'Husband ID', 'Husband Name', 'Wife ID', 'Wife Name', 'Children')

    def __init__(self, fam_id):
        self.fam_id = fam_id
        self.marr_dt = None
        self.div_dt = None
        self.husb_id = ''
        self.wife_id = ''
        self.chil_id = set()  # chil_id = set of indi_id

    def mongo_data(self):
        """ return a dictionary with mongodb data for database"""
        return {
            '_id': self.fam_id,
            'cat': 'fam',
            'marr_dt': self.marr_dt,
            'div_dt': self.div_dt,
            'husb_id': self.husb_id,
            'wife_id': self.wife_id,
            'chil_id': list(self.chil_id)
        }

    def pp_row(self):
        """ return a data sequence:
            [ID, Marr, Div, Husb_id, Wife_id, Chil_ids]
        """
        return self.fam_id, self.marr_dt.strftime('%Y-%m-%d'), self.div_dt.strftime('%Y-%m-%d') if self.div_dt else 'NA', \
            self.husb_id, self.wife_id, ', '.join(self.chil_id) if self.chil_id else 'NA'


def main():
    """ Entrance"""
    gdm = Gedcom('/Users/benjamin/Documents/Python_Scripts/SSW555/GEDCOM_files/proj01.ged')
    gdm.pretty_print()
    gdm.us65536_example()

if __name__ == "__main__":
    main()
        
