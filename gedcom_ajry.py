""" GEDCOM error distinguish"""

import os
import re
import json
import unittest
import sys

from tabulate import tabulate
from datetime import datetime
from collections import defaultdict
from mongo_db import MongoDB
      

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

        self.mongo_instance = MongoDB()

        self.data_parser()
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
                    curr_entity[attr]['first'] = regex_obj.group(1)
                    curr_entity[attr]['last'] = regex_obj.group(2)

                elif tag in ('CHIL', 'FAMS'):  # beware that the the value of CHIL is a set
                    curr_entity[attr].add(arg)

                else:
                    curr_entity[attr] = arg
        cat_cont[curr_cat][curr_id] = curr_entity

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
            husb_nm = ', '.join([self.indis[husb_id].name['last'], self.indis[husb_id].name['first']])
            wife_nm = ', '.join([self.indis[wife_id].name['last'], self.indis[wife_id].name['first']])
            fams_rows.append((id_, marr, div, husb_id, husb_nm, wife_id, wife_nm, chil_ids))  

        print(tabulate(fams_rows, headers=Family.pp_header, tablefmt='fancy_grid', showindex='never'))  

    def _find_children(self, indi):
        """ return all of the children objects of given indi_id"""
        children = []

        for fam_id in indi.fam_s:
            children.extend(self.fams[fam_id].chil_id)  # extend all children's id(string) of this individual

        return [self.indis[i] for i in children]  # list of individual objects

    def _find_siblings(self, indi):
        """ return all of the siblings objects of given indi_id"""
        siblings = []
        if not indi.fam_c:
            return []
        else:
            siblings.extend(self.fams[indi.fam_c].chil_id)

        return [self.indis[i] for i in siblings]

    def insert_to_mongo(self):
        """ invoke this method everytime at the start of the userstory
            create a mongodb and insert the data
            store the mongo client as an instance attr
            return a collection reference for use in user story method
        """
        indi_mg = [i.mongo_data() for i in self.indis.values()]  # create data set for insert_many()
        fam_mg = [f.mongo_data() for f in self.fams.values()]
        
        mongo_instance = MongoDB()
        
        entts = mongo_instance.get_collection("entity")
        entts.insert_many([*indi_mg, *fam_mg])
        
        return entts


    """ ----------------------------------------- """
    """                                           """
    """ User Stories' methods listed as following """
    """                                           """
    """ ----------------------------------------- """

    def us02_birth_before_marriage(self):
        """ Ray, Feb 22th, 2019
            US02: Birth before marriage
            Birth should occur before marriage of an individual
        """

        flag = False    #For Testing 
        for uid, indi in self.indis.items(): 
            temp = indi.birt_dt
            temp2 = ""
            for temp2 in indi.fam_s:
                break
            for fid, fam in self.fams.items():
            
                if temp2 == fam.fam_id: 
                    if temp > fam.marr_dt: 
                        print("Error! Marriage Date is greater than Birth Date for Family: ",fam.fam_id)
                        return False
                    else: 
                        print('Valid Marriage for Family: ', fam.fam_id)
                        flag = True
        
        return flag

        
    def us11_no_bigamy(self): 
        """ Ray, Feb 22th, 2019
            US11: No bigamy
            Married person should not be in another marriage
        """

        flag = False
        for indi, fam_s in self.indis.items():
            dummy = ""
            temp = ""
            for temp in fam_s.fam_s:
                break
            for a in fam_s.fam_s: 
                dummy = dummy + a
            for fid, fam in self.fams.items(): 
                if fam.fam_id == temp: 
                    if sys.getsizeof(dummy) > 53 and fam.div_dt != None:
                        print("Error! Cannot have multiple spouses!")
                        return False
                    else: 
                        print("Good Civilian!")
                        flag = True
        
        return flag

    def us01_date_validate(self):
        """ Javer, Feb 19, 2019
            Date Validate
            Dates (birth, marriage, divorce, death) should not be after the current date
        """
        current_time = datetime.now()
        current_time = datetime.strptime("2000-01-01", "%Y-%m-%d") # for test
        cond = {
            "$or": [
                {"birt_dt": {"$gt": current_time}},
                {"deat_dt": {"$gt": current_time}},
                {"marr_dt": {"$gt": current_time}},
                {"div_dt": {"$gt": current_time}},
            ]
        }

        error_mes = ""
        result_of_docs = MongoDB().get_collection('entity').find(cond)

        for doc in result_of_docs:
            tmp_str = ""
            if doc['cat'] == 'fam':
                # for family
                if doc['marr_dt'] is not None and doc['marr_dt'] > current_time:
                    tmp_str += f"marriage date [{doc['marr_dt']}], "
                if doc['div_dt'] is not None and doc['div_dt'] > current_time:
                    tmp_str += f"divorice date [{doc['div_dt']}]"
                error_mes += f"Family entity ID: {doc['_id']}, have incorrect {tmp_str}\n"

            if doc['cat'] == 'indi':
                # for individual
                if doc['birt_dt'] is not None and doc['birt_dt'] > current_time:
                    tmp_str += f"birth date [{doc['birt_dt']}], "
                if doc['deat_dt'] is not None and doc['deat_dt'] > current_time:
                    tmp_str += f"deadth date [{doc['deat_dt']}]"
                error_mes += f"Individual entity ID: {doc['_id']}, have incorrect {tmp_str}\n"
        
        print(f"Tested current_date: {current_time}")
        print(error_mes)

    def us22_unique_ids(self):
        """ Javer, Feb 23, 2019
            Unique Ids
            To make sure all individual IDs should be unique and all family IDs should be unique 
        """
        collection = MongoDB().get_collection('entity')

        # for indi
        indi_cond = {'cat': 'indi'}
        result_of_indi_docs = collection.find(indi_cond)
        dict_of_indi = {}
        for doc in result_of_indi_docs:
            # if doc['_id'] == "@I1@": # test for id conflict
                # doc['_id'] = "@I2@"
            if doc['_id'] in dict_of_indi.keys():
                print(f"Conflict of individual id: {doc['_id']}")
            else:
                dict_of_indi[doc['_id']] = doc

        # for fam
        fam_cond = {'cat': 'fam'}
        result_of_fam_docs = collection.find(fam_cond)
        dict_of_fam = {}
        for doc in result_of_fam_docs:
            # if doc['_id'] == "@F1@": # test for id conflict
            #     doc['_id'] = "@F2@"
            if doc['_id'] in dict_of_fam.keys():
                print(f"Conflict of individual id: {doc['_id']}")
            else:
                dict_of_fam[doc['_id']] = doc

    def us05_marriage_before_death(self):
        """ John February 23, 2018
            US05: Marriage Before Death
            This method checks if the marriage date is before the husband's or wifes's death date or not.
            Method prints an error if anomalies are found.
        """
        for fam in self.fams.values():
            for indi in self.indis.values():
                if (fam.husb_id==indi.indi_id):
                    husb_dt = indi.deat_dt
                elif(fam.wife_id==indi.indi_id):
                    wife_dt = indi.deat_dt
            if(husb_dt !=None and fam.marr_dt>husb_dt):
                print("Error, death before marriage of husband with id : ", fam.husb_id)
            if(wife_dt !=None and fam.marr_dt>wife_dt):
                print("Error, death before her marriage of wife with id : ", fam.wife_id)
                              
    def us03_birth_before_death(self):
        """ John February 18th, 2018
            US03: Birth before Death
            This method checks if the birth date comes before the death date or not. 
            Method prints an error if anomalies are found.
        """
        for people in self.indis.values():
            if(people.deat_dt==None):
                continue
            elif(people.birt_dt>people.deat_dt):
                print("Error, death date after birth date for individual with id : ", people.indi_id)

    def us06_divorce_before_death(self, debug=False):
        """ Benji, Feb 21st, 2019
            US06: Death before divorce
            Divorce can only occur before death of both spouses
        """
        err_msg_lst = []  # store each group of error message as a tuple
        
        for fam in self.fams.values():
            if fam.div_dt:    
                husb, wife = self.indis[fam.husb_id], self.indis[fam.wife_id]

                if husb.deat_dt and husb.deat_dt < fam.div_dt:
                    err_msg_lst.append((fam.fam_id, fam.div_dt.strftime('%m/%d/%y'), husb.indi_id, 'husband', husb.name, husb.deat_dt.strftime('%m/%d/%y')))

                if wife.deat_dt and wife.deat_dt < fam.div_dt:
                    err_msg_lst.append((fam.fam_id, fam.div_dt.strftime('%m/%d/%y'), wife.indi_id, 'wife', wife.name, wife.deat_dt.strftime('%m/%d/%y')))

        if debug:
            return err_msg_lst
        else:
            for err_msg in err_msg_lst:
                Error.err06(*err_msg)

    def us20_aunts_and_uncle(self, debug=False):
        """ Benji, Feb 22th, 2019
            US20: Uncles and Aunts
            Aunts and uncles should not marry their nieces or nephews
            Definition of Aunt&Uncle: Sibling of an individual's parent
        """
        err_msg_lst = []

        for indi in self.indis.values():
            children = self._find_children(indi)
            siblings = self._find_siblings(indi)

            for sibling in siblings:
                for child in children:
                    if sibling.fam_s & child.fam_s:  # as fam_s is a set, python has this intersection shortcut, DOPE
                        err_msg_lst.append((indi.indi_id, indi.name, child.indi_id, child.name, sibling.indi_id, sibling.name))

        if debug:
            return err_msg_lst
        else:
            for err_msg in err_msg_lst:
                Warn.warn20(*err_msg)



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

    def pp_row(self):
        """ Return a row for command line pretty print"""
        raise NotImplementedError('Method hasn\'t been implemented yet.')

class Individual(Entity):
    """ Represent the individual entity in the GEDCOM file"""

    pp_header = ('ID', 'Name', 'Gender', 'Birthday', 'Age', 'Alive', 'Death', 'Child', 'Spouse')

    def __init__(self, indi_id):
        self.indi_id = indi_id
        self.name = {'first': '', 'last': ''}
        self.sex = ''
        self.birt_dt = None
        self.deat_dt = None
        self.fam_c = ''
        self.fam_s = set()

    @property
    def age(self):
        """ return the age of this individual"""
        if self.birt_dt:
            age_td = datetime.today() - self.birt_dt if not self.deat_dt else self.deat_dt - self.birt_dt
            return (age_td.days + age_td.seconds // 86400) // 365
        else:
            return 'No birth date.'

    def pp_row(self):
        """ return a data sequence:
            [ID, Name, Gender, Birthday, Age, Alive, Death, Child, Spouse]
        """
        return self.indi_id, ', '.join([self.name['last'], self.name['first']]), self.sex, \
                self.birt_dt.strftime('%Y-%m-%d'), self.age, True if not self.deat_dt else False, self.deat_dt.strftime('%Y-%m-%d') if self.deat_dt else 'NA', \
                self.fam_c if self.fam_c else 'NA', ', '.join(self.fam_s) if self.fam_s else 'NA' 

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

    def pp_row(self):
        """ return a data sequence:
            [ID, Marr, Div, Husb_id, Wife_id, Chil_ids]
        """
        return self.fam_id, self.marr_dt.strftime('%Y-%m-%d'), self.div_dt.strftime('%Y-%m-%d') if self.div_dt else 'NA', \
            self.husb_id, self.wife_id, ', '.join(self.chil_id) if self.chil_id else 'NA'

class Error:
    """ A class used to bundle up all of the error message
        the method naming pattern is err[us_ID](*args, *kwargs)
    """
    header = 'Error {}: '

    @classmethod
    def err06(cls, fam_id='', div_dt='', spouse_id='', spouse='', spouse_name='', spouse_deat_dt='', VERBOSE=False):
        """ return error message for User Stroy 06"""
        us_id = 'US06'
        if VERBOSE:
            print(cls.header.format(us_id) + f'The {spouse} of family {fam_id}, {spouse_name}({spouse_id}), died before divorce.' + \
                f'\n\t\t\tDeath date of {spouse_name}: {spouse_deat_dt}' + f'\n\t\t\tDivorce date of family {fam_id}: {div_dt}')
        print(cls.header.format(us_id) + f'The {spouse} of family {fam_id}, {spouse_name}({spouse_id}), died before divorce.')

class Warn:
    """ A class used to bundle up all of the warning message
        the method naming pattern is warn[us_ID](*args, *kwargs)
    """
    header = 'Warning {}: '

    @classmethod
    def warn20(cls, indi_id, indi_name, child_id, child_name, sibling_id, sibling_name):
        """ return warning message for User Story 20"""
        us_id = 'US20'
        indi_nm = ' '.join([indi_name['first'], indi_name['last']])  
        child_nm = ' '.join([child_name['first'], child_name['last']])  
        sibling_nm = ' '.join([sibling_name['first'], sibling_name['last']])

        print(
            cls.header.format(us_id) + \
            f'The child of {indi_nm}({indi_id}), {child_nm}({child_id}), is married with the sibling of {indi_nm}({indi_id}), {sibling_nm}({sibling_id})'
            )

def main():
    """ Entrance"""

    gdm = Gedcom('./GEDCOM_files/proj01.ged')
    
    # keep the three following lines for the Mongo, we may use this later.
    # mongo_instance = MongoDB()
    # mongo_instance.delete_database()
    # gdm.insert_to_mongo()
    
    """ User Stories for the Spint1 """
    # Javer
    gdm.us01_date_validate()
    gdm.us22_unique_ids()

    # Benji
    gdm = Gedcom('GEDCOM_files/us20_nephew_marr_aunt.ged')
    gdm.us06_divorce_before_death()
    gdm.us20_aunts_and_uncle()

    # Ray
    gdm.us03_birth_before_marriage()
    gdm.us11_no_bigamy()

    # John
    gdm.us03_birth_before_death()
    gdm.us05_marriage_before_death()

if __name__ == "__main__":
    main()
    # unittest.main(exit=False, verbosity=2)
        
