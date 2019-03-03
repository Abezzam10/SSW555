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


        self.errors = {
                        'us22': []
                    }  # this dictionary is used to store the error/anomally that are supposed to find during the interpretation of the GEDCOM file

        self.mongo_instance = MongoDB()
        self.formatted_data = {"family":{}, "individual":{}}    # formatted data into db's structure

        self.data_parser()
        self.lst_to_obj()


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
                    
                    if curr_id in cat_cont[curr_cat]:  # NOTE: check for US22
                        self.errors['us22'].append((curr_id, curr_cat))
                    else:
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

                elif tag in ('CHIL', 'FAMS'):  # 'CHIL' and 'FAMS' are sets
                    curr_entity[attr].add(arg)

                else:
                    curr_entity[attr] = arg
        cat_cont[curr_cat][curr_id] = curr_entity

    def format_data_structure(self):
        """ format the data into db structure
        """
        for fam_id, family in self.fams.items():
            tmp_dict = {}
            tmp_dict['fam_id'] = fam_id
            tmp_dict['members'] = []
            tmp_dict['husb_id'] = family.husb_id
            tmp_dict['wife_id'] = family.wife_id
            tmp_dict['marr_dt'] = family.marr_dt
            tmp_dict['div_dt'] = family.div_dt
            tmp_dict['both_alive'] = None

            if family.husb_id in self.indis and family.wife_id in self.indis:

                if self.indis[family.husb_id]['deat_dt'] == None and self.indis[family.wife_id]['deat_dt'] == None:
                    tmp_dict['both_alive'] = True
                else:
                    tmp_dict['both_alive'] = False
   
            self.formatted_data['family'][fam_id] = tmp_dict

        for indi_id, individual in self.indis.items():
            tmp_dict = {}
            tmp_dict['indi_id'] = indi_id
            tmp_dict['name'] = individual.name
            tmp_dict['sex'] = individual.sex
            tmp_dict['birt_dt'] = individual.birt_dt
            tmp_dict['deat_dt'] = individual.deat_dt
            tmp_dict['age'] = individual.age
            tmp_dict['child_of_family'] = individual.fam_c
            tmp_dict['spous_of_family'] = list(individual.fam_s)
            
            self.formatted_data['individual'][indi_id] = tmp_dict
            
            # figure out which fam_id is the current individual belongs
            if individual.fam_c != "":
                self.formatted_data['family'][individual.fam_c]['members'].append({"indi_id": indi_id, "hierarchy": 1})
            if len(individual.fam_s) != 0:
                for fam_id in individual.fam_s:
                   self.formatted_data['family'][fam_id]['members'].append({"indi_id": indi_id, "hierarchy": 0})

        # print(self.formatted_data)

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
        # Todo: When do the refactoring, we will remvoe the following commented lines
        # indi_mg = [i.mongo_data() for i in self.indis.values()]  # create data set for insert_many()
        # fam_mg = [f.mongo_data() for f in self.fams.values()]
        
        # mongo_instance = MongoDB()
        
        # entts = mongo_instance.get_collection("entity")
        # entts.insert_many([*indi_mg, *fam_mg])
        
        # return entts
        self.format_data_structure()
        fams = [f for f in self.formatted_data['family'].values()]
        indis = [i for i in self.formatted_data['individual'].values()]
        self.mongo_instance.get_collection("family").insert_many(fams)
        self.mongo_instance.get_collection("individual").insert_many(indis)

    def _earlier_deat_dt_in_fam(self, fam_id):
        """ return the smaller(earlier) deat_dt of the given indi_id"""
        fam = self.fams[fam_id]
        husb, wife = self.indis[fam.husb_id], self.indis[fam.wife_id]

        if husb.deat_dt and wife.deat_dt:
            return min(husb.deat_dt, wife.deat_dt)  # return the smaller(earlier) datetime
        else:
            return husb.deat_dt or wife.deat_dt  # 3 possible return values: husb.deat_dt, wife.deat_dt, None

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
                        print("Error US02: Marriage Date is greater than Birth Date for Family: ",fam.fam_id)
                        return False
                    else: 
                        flag = True
        
        return flag
        
    def us11_no_bigamy(self, debug=False): 
        """ Ray, Feb 22th, 2019
            US11: No bigamy
            Married person should not be in another marriage
            :: refactored at Feb 27th by Benji
        """
        
        #flag = False
        #for indi, fam_s in self.indis.items():
        #    dummy = ""
        #    temp = ""
        #    for temp in fam_s.fam_s:
        #        break
        #    for a in fam_s.fam_s: 
        #        dummy = dummy + a
        #    for fid, fam in self.fams.items(): 
        #        if fam.fam_id == temp: 
        #            if sys.getsizeof(dummy) > 53 and fam.div_dt != None:
        #                print("Error US11: Cannot have multiple spouses!")
        #                return False
        #            else: 
        #                flag = True
        #
        #return flag

        err_msg_dct = defaultdict(set) 
        
        for indi in self.indis.values():
            if len(indi.fam_s) > 1:  # multi-marriage
       
                marr_range_tups = []  # [(fam_id, marr_start, marr_end), ...]
                for fam in [self.fams[fam_id] for fam_id in indi.fam_s]:
                    # for each marriage, it starts at marr_dt, it ends at either divorce or death of one of the spouse
                    marr_range_tups.append((fam.fam_id, fam.marr_dt, fam.div_dt or self._earlier_deat_dt_in_fam(fam.fam_id)))
                prev_fam_id, prev_start, prev_end = None, None, None
                for fam_id, start, end in sorted(marr_range_tups, key=lambda x: x[1]):
                    if prev_fam_id is None:
                        prev_fam_id, prev_start, prev_end = fam_id, start, end
                        continue

                    if prev_end is None or (prev_end is not None and prev_end > start):
                        err_msg_dct['|'.join((indi.name['first'], indi.name['last'], indi.indi_id))].update((prev_fam_id, fam_id))
                        
        if debug:
            return err_msg_dct
        else:
            Error.err11(err_msg_dct)

    def us01_date_validate(self):
        """ Javer, Feb 19, 2019
            Date Validate
            Dates (birth, marriage, divorce, death) should not be after the current date
        """
        current_time = datetime.now()
        # current_time = datetime.strptime("2000-01-01", "%Y-%m-%d") # for test
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
                error_mes += f"Family entity ID: {doc['id']}, have incorrect {tmp_str}\n"

            if doc['cat'] == 'indi':
                # for individual
                if doc['birt_dt'] is not None and doc['birt_dt'] > current_time:
                    tmp_str += f"birth date [{doc['birt_dt']}], "
                if doc['deat_dt'] is not None and doc['deat_dt'] > current_time:
                    tmp_str += f"deadth date [{doc['deat_dt']}]"
                error_mes += f"Individual entity ID: {doc['id']}, have incorrect {tmp_str}\n"
        
        print(f"Tested current_date: {current_time}")
        print(error_mes)

    def us22_unique_ids(self, debug=False):
        """ Javer, Feb 23, 2019
            Unique Ids
            To make sure all individual IDs should be unique and all family IDs should be unique 
        """
        if debug:
            return self.errors['us22']
        else:
            for err_msg in self.errors['us22']:
                Error.err22(*err_msg)          

    def us05_marriage_before_death(self):
        """ John February 23, 2018
            US05: Marriage Before Death
            This method checks if the marriage date is before the husband's or wifes's death date or not.
            Method prints an error if anomalies are found.
        """
        error_message_list = []
        
        for fam in self.fams.values():
            for indi in self.indis.values():
                
                if fam.husb_id == indi.indi_id:
                    husb_dt = indi.deat_dt
                if fam.wife_id == indi.indi_id:
                    wife_dt = indi.deat_dt
            
            if husb_dt is not None and fam.marr_dt > husb_dt:
                print("Error US05: death before marriage of husband with id : ", fam.husb_id)
                error_message_list.append("Error, death before marriage of husband with id : "+fam.husb_id)
            
            if wife_dt is not None and fam.marr_dt > wife_dt:
                print("Error US05: death before her marriage of wife with id : ", fam.wife_id)
                error_message_list.append("Error, death before her marriage of wife with id : "+fam.wife_id)
        
        return error_message_list

    def us03_birth_before_death(self):
        """ John February 18th, 2018
            US03: Birth before Death
            This method checks if the birth date comes before the death date or not. 
            Method prints an error if anomalies are found.
        """
        error_message_list=[]
        for people in self.indis.values():
            if people.deat_dt == None:
                continue
            elif people.birt_dt > people.deat_dt:
                print("Error US03: death date before birth date for individual with id : "+people.indi_id)
                error_message_list.append("Error, death date before birth date for individual with id : "+people.indi_id)
        return error_message_list

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

    def us04_marr_b4_div(self, debug=False):
        """ John, <time you manipulate the code>
            US04: Marriage before divorce
            <definition of the user story>
        """

    def us07_less_than_150_yrs(self, debug=False):
        """ Benji, <time you manipulate the code>
            US07: Less than 150 years old
            <definition of the user story>
        """
    
    def us08_birt_b4_marr_of_par(self, debug=False):
        """ Ray, <time you manipulate the code>
            US08: Birth before marriage of parents
            <definition of the user story>
        """

    def us13_sibling_spacing(self, debug=False):
        """ John, <time you manipulate the code>
            US13: Siblings spacing
            <definition of the user story>
        """

    def us14_multi_birt_less_than_5(self, debug=False):
        """ Javer, <time you manipulate the code>
            US14: Multiple births <= 5
            <definition of the user story>
        """
        err_msg_lst = []  # store each group of error message as a tuple
        
        cond = [
            {"$unwind": "$members"},
            {"$match": {"members.hierarchy": {"$eq": 1}}},
            {
                "$lookup":{
                    "from": "individual",
                    "localField": "members.indi_id",
                    "foreignField": "indi_id",
                    "as": "members_info"
                }
            },
            {"$group": {"_id": "$fam_id", "count": {"$sum": 1}}},
            {"$match": {"count": {"$gte": 3}}},
        ]
        count_of_sibling = self.mongo_instance.get_collection('family').aggregate(cond)
        
        for count in count_of_sibling:
            if count['count'] >= 3:
                result_of_indis = self.mongo_instance.get_collection('individual').find({"child_of_family": count['_id']})
                for indi in result_of_indis:
                    print(indi)
            break  

        # if debug:
        #     return err_msg_lst
        # else:
        #     for err_msg in err_msg_lst:
        #         print(err_msg)

    def us16_male_last_name(self, debug=False):
        """ Javer, <Mar 3, 2019>
            US16: Male last names
            To check each male has the last name within each family
        """
        err_msg_lst = []  # store each group of error message as a tuple
        cond = [
            {
                "$lookup":{
                    "from": "individual",
                    "localField": "members.indi_id",
                    "foreignField": "indi_id",
                    "as": "members_info"
            }
        }]
        result_of_docs = self.mongo_instance.get_collection('family').aggregate(cond)
        
        for doc in result_of_docs:
            tmp_last_name = ""
            diff_male_last_name_with_indi_id = {}
            for member in doc['members_info']:
                if member['sex'] == 'M':
                    if tmp_last_name == "":
                        tmp_last_name = member['name']['last']
                        diff_male_last_name_with_indi_id[member['name']['last']] = member['indi_id']
                        
                    else:
                        if member['name']['last'] != tmp_last_name:
                            if member['name']['last'] not in diff_male_last_name_with_indi_id:
                                diff_male_last_name_with_indi_id[member['name']['last']] = member['indi_id']

            if len(diff_male_last_name_with_indi_id) > 1:
                err_msg_lst.append(f"Error for US16: Family ({doc['fam_id']}) contains different male last names: {','.join(diff_male_last_name_with_indi_id.values())}, with values: {','.join(diff_male_last_name_with_indi_id)}")

        if debug:
            return err_msg_lst
        else:
            for err_msg in err_msg_lst:
                print(err_msg)

    def us23_unique_name_and_birt(self, debug=False):
        """ Ray, <time you manipulate the code>
            US23: Unique name and birth date
            <definition of the user story>
        """

    def us26_corrspnding_entries(self, debug=False):
        """ Benji, <time you manipulate the code>
            US26: Corresponding entries
            <definition of the user story>
        """

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

    def mongo_data(self):
        """ return a dictionary with mongodb data for database"""
        return {
            'id': self.indi_id,
            'cat': 'indi',  # only used for mongodb to distinguish entity catagory
            'name': self.name,
            'sex': self.sex,
            'birt_dt': self.birt_dt,
            'deat_dt': self.deat_dt,
            'age': self.age,
            'fam_c': self.fam_c,
            'fam_s': list(self.fam_s)
        }

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
 
    def mongo_data(self):
        """ return a dictionary with mongodb data for database"""
        return {
            'id': self.fam_id,
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

    @classmethod
    def err22(cls, entt_id, entt_cat):
        """ return error message for User Stroy 22"""
        us_id = 'US22'
        cat = 'individual' if entt_cat == 'INDI' else 'family' 
        print(cls.header.format(us_id) + f'The ID of {cat} {entt_id} was existed already. Entity omitted during the build')

    @classmethod
    def err11(cls, err_msg_dct):
        """ print error message for User Story 11
            name_id: 'first|last|id'
            fam_info: set of fam_id
        """
        us_id = 'US11'
        for name_id, fam_info in err_msg_dct.items():
            first, last, indi_id = name_id.split('|')
            print(Error.header.format(us_id) + 'The individual {0}, {1} {2}, is in marriage {3} at the same time.'.format(indi_id, first, last, ', '.join(fam_info)))


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

    # gdm = Gedcom('./GEDCOM_files/integrated_no_err.ged')
    gdm = Gedcom('./GEDCOM_files/integration_all_err.ged')
    
    # keep the three following lines for the Mongo, we may use this later.
    mongo_instance = MongoDB()
    # mongo_instance.drop_collection("family")
    # mongo_instance.drop_collection("individual")
    # gdm.insert_to_mongo()
    # mongo_instance.delete_database()
    
    """ User Stories for the Spint2 """
    # Javer
    gdm.us14_multi_birt_less_than_5()
    # gdm.us16_male_last_name()
    
    # # John
    # gdm.us03_birth_before_death()
    # gdm.us05_marriage_before_death()

    # # Benji
    # gdm.us06_divorce_before_death()
    # gdm.us20_aunts_and_uncle()

    # # Ray
    # gdm.us02_birth_before_marriage()
    # gdm.us11_no_bigamy()

    

if __name__ == "__main__":
    main()
    # unittest.main(exit=False, verbosity=2) 
