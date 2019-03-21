""" GEDCOM error distinguish"""

import os
import re
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
        self.formatted_data = {"family":{}, "individual":{}}    # formatted data into db's structure

        # this dictionary is used to store the error/anomally messages
        self.msg_collections = {

            'err': {
                'header': 'Error {}: ',  # this is changable when the error line user story add in
                'msg_container': {  # key: user story ID, value: fmt_str, tokens.

                    'US06': {
                        'fmt_msg': '{}, the {} of {}, died before divorce. Death date is {}. Divorce date is {}.',
                        'tokens': []  # tokens[i] = (name, 'wife'|'husband', fam_id, deat_dt, div_dt)
                    },

                    'US22': {
                        'fmt_msg': 'The ID of {} {} was existed already. Entity omitted during the build',
                        'tokens': []  # tokens[i] = ('INDI'|'FAM', entt_id)
                    },

                    'US11': {
                        'fmt_msg': 'The individual {0}, {1}, is in marriage {2} at the same time.',
                        'tokens': []  # tokens[i] = (indi_id, name, str_of_all_bigamy)
                    },

                    'US07': {
                        'fmt_msg': 'The individual {}, {} is over 150 years old, the person is {} years old.',
                        'tokens': []  # tokens[i] = (indi_id, name, age)
                    },

                    'US03': {
                        'fmt_msg': 'Death date before birth date for individual, {} with id : {}',
                        'tokens': []   #tokens[i] = (name, indi_id)
                    },

                    'US05': {
                        'fmt_msg': 'Death before marriage of {}, {} with individual id : {} and family id: {}',
                        'tokens': []   #tokens[i] =(husband/wife, name, indi_id, fam_id)
                    },

                    'US04': {
                        'fmt_msg': 'Divorce date before marriage date of family with id : {}',
                        'tokens': []   #tokens[i] = (fam_id)
                    }
                }
            },

            'anomaly': {
                'header': 'Anomaly {}: ',
                'msg_container': {

                    'US20': {
                        'fmt_msg': 'The child of {0}({1}), {2}({3}), is married with the sibling of {0}, {4}({5})',
                        'tokens': [] # tokens[i] = (indi_nm, indi_id, child_nm, child_id, sibling_nm, sibling_id)
                    },

                    'US13': {
                        'fmt_msg': '{} with id: {} and {} with id : {} are siblings and their birth dates are {} days apart.',
                        'tokens': []     #tokens[i] = (sibling1_name, sibling1_id, sibling2_name, sibling2_id, difference of birth date in days)
                    }
                }
            }
        }

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
                        self.msg_collections['err']['msg_container']['US22']['tokens'].append((curr_id, curr_cat))
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
        indis = {indi_id: indi.mongo_data() for indi_id, indi in self.indis.items()}  # indi.mongo_data() return a formatted dict
        fams = {fam_id: fam.mongo_data() for fam_id, fam in self.fams.items()}  # dictionary comprehension. COMPREHENSION FOR ALL!!! LMAO

        # update the fams[fam_id][both_alive] field
        for fam in fams.values():
            fam['both_alive'] = bool(not indis[fam['husb_id']]['deat_dt'] and not indis[fam['wife_id']]['deat_dt'])  # both husb and wife don't have a deat_dt

        self.formatted_data['family'] = fams
        self.formatted_data['individual'] = indis

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
        # TODO: When do the refactoring, we will remvoe the following commented lines
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

    def msg_print(self):
        """ print all error and anomaly messages"""
        for cat in 'err', 'anomaly':  # hardcode the order
            for us_id in sorted(self.msg_collections[cat]['msg_container']):  # sort the user story id
                for token in self.msg_collections[cat]['msg_container'][us_id]['tokens']:
                    print(
                        self.msg_collections[cat]['header'].format(us_id) +
                        self.msg_collections[cat]['msg_container'][us_id]['fmt_msg'].format(*token)
                    )

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
                        print("Error US02: Marriage Date is greater than Birth Date for Family: ", fam.fam_id)
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
        
        for indi in self.indis.values():
            if len(indi.fam_s) > 1:  # multi-marriage

                bigamy_fam = set()

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
                        bigamy_fam.update((prev_fam_id, fam_id))
                
                if bigamy_fam:
                    fmt_str_bigamy = ' and '.join(sorted(bigamy_fam))
                    self.msg_collections['err']['msg_container']['US11']['tokens'].append(
                        (
                            indi.indi_id,
                            ' '.join((indi.name['first'], indi.name['last'])),
                            fmt_str_bigamy
                        )
                    )
                        
        if debug:
            return self.msg_collections['err']['msg_container']['US11']['tokens']

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
            return self.msg_collections['err']['msg_container']['US22']['tokens']       

    def us05_marriage_before_death(self, debug=False):
        """ John February 23, 2018
            US05: Marriage Before Death
            This method checks if the marriage date is before the husband's or wifes's death date or not.
            Method prints an error if anomalies are found.
        """
#        error_message_list = []
        
        for fam in self.fams.values():
            for indi in self.indis.values():
                
                if fam.husb_id == indi.indi_id:
                    husb_dt = indi.deat_dt
                    husb_name = ' '.join((indi.name['first'], indi.name['last']))
                    husb_id = indi.indi_id

                if fam.wife_id == indi.indi_id:
                    wife_dt = indi.deat_dt
                    wife_name = ' '.join((indi.name['first'], indi.name['last']))
                    wife_id = indi.indi_id

            if husb_dt is not None and fam.marr_dt > husb_dt:
                self.msg_collections['err']['msg_container']['US05']['tokens'].append(
                    (
                        'husband',
                        husb_name,
                        husb_id,
                        fam.fam_id
                    )
                )
#                print("Error US05: death before marriage of husband with id : ", fam.husb_id)
#                error_message_list.append("Error, death before marriage of husband with id : "+fam.husb_id)
            
            if wife_dt is not None and fam.marr_dt > wife_dt:
                self.msg_collections['err']['msg_container']['US05']['tokens'].append(
                    (
                        'wife',
                        wife_name,
                        wife_id,
                        fam.fam_id
                    )
                )
#                print("Error US05: death before her marriage of wife with id : ", fam.wife_id)
#                error_message_list.append("Error, death before her marriage of wife with id : "+fam.wife_id)
                
        if debug:
            return self.msg_collections['err']['msg_container']['US05']['tokens']

    def us03_birth_before_death(self, debug=False):
        """ John February 18th, 2018
            US03: Birth before Death
            This method checks if the birth date comes before the death date or not. 
            Method prints an error if anomalies are found.
        """
#        error_message_list = []
        for people in self.indis.values():
            if people.deat_dt is None:
                continue
            elif people.birt_dt > people.deat_dt:
                self.msg_collections['err']['msg_container']['US03']['tokens'].append(
                    (
                        ' '.join((people.name['first'], people.name['last'])),
                        people.indi_id
                    )
                )
 #               print("Error US03: death date before birth date for individual with id : "+people.indi_id)
 #               error_message_list.append("Error, death date before birth date for individual with id : "+people.indi_id)
        if debug:
            return self.msg_collections['err']['msg_container']['US03']['tokens']

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
                    self.msg_collections['err']['msg_container']['US06']['tokens'].append(
                        (
                            ' '.join((husb.name['first'], husb.name['last'])),
                            'husband',
                            fam.fam_id,
                            husb.deat_dt.strftime('%m/%d/%y'),
                            fam.div_dt.strftime('%m/%d/%y')
                        )
                    )

                if wife.deat_dt and wife.deat_dt < fam.div_dt:
                    self.msg_collections['err']['msg_container']['US06']['tokens'].append(
                        (
                            ' '.join((wife.name['first'], wife.name['last'])),
                            'wife',
                            fam.fam_id,
                            wife.deat_dt.strftime('%m/%d/%y'),
                            fam.div_dt.strftime('%m/%d/%y')
                        )
                    )

        if debug:
            return self.msg_collections['err']['msg_container']['US06']['tokens']

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
                        self.msg_collections['anomaly']['msg_container']['US20']['tokens'].append(
                            (
                                ' '.join((indi.name['first'], indi.name['last'])),
                                indi.indi_id,
                                ' '.join((child.name['first'], child.name['last'])),
                                child.indi_id,
                                ' '.join((sibling.name['first'], sibling.name['last'])),
                                sibling.indi_id,
                            )
                        )

        if debug:
            return self.msg_collections['anomaly']['msg_container']['US20']['tokens']

    def us04_marr_b4_div(self, debug=False):
        """ John, March 20th, 2019
            US04: Marriage before divorce
            Marriage should occur before divorce of spouses, and divorce can only occur after marriage
        """
        for fam in self.fams.values():
            if (fam.div_dt==None):
                continue
            elif(fam.marr_dt>fam.div_dt):
                self.msg_collections['err']['msg_container']['US04']['tokens'].append(
                            (
                                fam.fam_id
                            )
                        )
        if debug:
            return self.msg_collections['err']['msg_container']['US04']['tokens']

    def us07_less_than_150_yrs(self, debug=False):
        """ Benji, March 4th, 2019
            US07: Less than 150 years old
            Death should be less than 150 years after birth for dead people, and 
            current date should be less than 150 years after birth for all living people
        """
        err_msg_lst = []
        for indi in self.indis.values():
            if indi.age >= 150:  # age >= 150
                self.msg_collections['err']['msg_container']['US07']['tokens'].append(
                    (
                        indi.indi_id,
                        ' '.join((indi.name['first'], indi.name['last'])),
                        indi.age
                    )
                )

        if debug:
            return self.msg_collections['err']['msg_container']['US07']['tokens']

    def us08_birt_b4_marr_of_par(self, debug=False):
        """ Ray, <time you manipulate the code>
            US08: Birth before marriage of parents
            <definition of the user story>
        """

    def us13_sibling_spacing(self, debug=False):
        """ John, 20th March, 2019
            US13: Siblings spacing
            Birth dates of siblings should be more than 8 months apart or less than 2 days apart
             (twins may be born one day apart, e.g. 11:59 PM and 12:02 AM the following calendar day)
        """
        siblings = []
        for indi in self.indis.values():
            flag = False
            for tuple in self.msg_collections['anomaly']['msg_container']['US13']['tokens']:
                if (indi.indi_id == tuple[1] or indi.indi_id == tuple[3]):
                    flag = True
            if flag:
                continue
            siblings = self._find_siblings(indi)
            for i in range(len(siblings)):
                for j in range(i+1,len(siblings)):
                    if(abs((siblings[i].birt_dt-siblings[j].birt_dt).days) < 274 and abs((siblings[i].birt_dt-siblings[j].birt_dt).days) > 1):
                        self.msg_collections['anomaly']['msg_container']['US13']['tokens'].append(
                            (
                                ' '.join((siblings[i].name['first'], siblings[i].name['last'])),
                                siblings[i].indi_id,
                                ' '.join((siblings[j].name['first'], siblings[j].name['last'])),
                                siblings[j].indi_id,
                                abs((siblings[i].birt_dt-siblings[j].birt_dt).days)
                            )
                        )
        if debug:
            return self.msg_collections['anomaly']['msg_container']['US13']['tokens']            

    def us14_multi_birt_less_than_5(self, debug=False):
        """ Javer, <time you manipulate the code>
            US14: Multiple births <= 5
            No more than five siblings should be born at the same time within a family
        """
        err_msg_lst = []  # store each group of error message as a tuple
        less_than = 5 # using 2 for testing

        # First, using hierarchy to count the number of sibling from a family which number is greater than 5 
        count_of_sibling_cond = [
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
            {"$match": {"count": {"$gte": less_than}}},
        ]
        count_of_sibling = self.mongo_instance.get_collection('family').aggregate(count_of_sibling_cond)
        
        for count in count_of_sibling:
            if count['count'] >= less_than:
                # Then, using birt_dt to group and count the individuals whithin a family that have the same birt year-month-day
                group_and_count_by_date_cond = [
                    {"$match": {"child_of_family": count['_id']}},
                    {"$project": {
                        "birt_dt": {"$substr":["$birt_dt", 0, 10]}, 
                        "indi_id": 1,
                        "child_of_family": 1
                    }},
                    {"$group": {
                        "_id": "$birt_dt", 
                        "count": {"$sum": 1}, 
                        "indi_ids": {"$push": "$indi_id"},
                        "fam_id": {"$first": "$child_of_family"}
                    }},
                    {"$match": {"count": {"$gte": less_than}}},
                ]

                result_of_indis = self.mongo_instance.get_collection('individual').aggregate(group_and_count_by_date_cond)
                for indi in result_of_indis:
                    err_msg_lst.append(f"Error for US14: Family ({indi['fam_id']}) contains multi birth greater than {less_than}, indi_id: [{', '.join(indi['indi_ids'])}]")

        if debug:
            return err_msg_lst
        else:
            for err_msg in err_msg_lst:
                print(err_msg)

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
                err_msg_lst.append(f"Error for US16: Family ({doc['fam_id']}) contains different male last names: {', '.join(diff_male_last_name_with_indi_id.values())}, with values: {','.join(diff_male_last_name_with_indi_id)}")

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
            'idni_id': self.indi_id,
            'name': self.name,
            'sex': self.sex,
            'birt_dt': self.birt_dt,
            'deat_dt': self.deat_dt,
            'age': self.age,
            'child_of_family': self.fam_c,
            'spous_of_family': list(self.fam_s)
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
            'fam_id': self.fam_id,
            'members':
                [{'indi_id': indi_id, 'hierarchy': 0} for indi_id in (self.husb_id, self.wife_id) if indi_id] + \
                [{'indi_id': indi_id, 'hierarchy': 1} for indi_id in self.chil_id if indi_id],  # put an if statement to ensure no '' is inside
            'husb_id': self.husb_id,
            'wife_id': self.wife_id,
            'marr_dt': self.marr_dt,
            'div_dt': self.div_dt,
            'both_alive': None
            }

    def pp_row(self):
        """ return a data sequence:
            [ID, Marr, Div, Husb_id, Wife_id, Chil_ids]
        """
        return self.fam_id, self.marr_dt.strftime('%Y-%m-%d'), self.div_dt.strftime('%Y-%m-%d') if self.div_dt else 'NA', \
            self.husb_id, self.wife_id, ', '.join(self.chil_id) if self.chil_id else 'NA'

def main():
    """ Entrance"""

    # gdm = Gedcom('./GEDCOM_files/integrated_no_err.ged')
    # gdm = Gedcom('./GEDCOM_files/integration_all_err.ged')
    gdm = Gedcom('./GEDCOM_files/us13/us13_within2days.ged')
    # keep the three following lines for the Mongo, we may use this later.
    # mongo_instance = MongoDB()
    # mongo_instance.drop_collection("family")
    # mongo_instance.drop_collection("individual")
    # gdm.insert_to_mongo()
    # mongo_instance.delete_database()
    
    """ User Stories for the Spint2 """
    # Javer
    # gdm.us14_multi_birt_less_than_5()
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

    gdm.us13_sibling_spacing()
    gdm.msg_print()

    

if __name__ == "__main__":
    main()
    # unittest.main(exit=False, verbosity=2) 
