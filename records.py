#!/usr/bin/env python

import os
import sys
import shutil
import glob
import shelve
import yaml
from datetime import datetime


bkp_dateformat = '%d-%m-%Y'

class Records():
    """Database functions.
    num_backups and backup_freq govern how many
    backups will be maintained and how frequently
    they will be created"""
    def __init__(self, db_file, index_file, passfile,
                 num_backups, backup_freq):
        self.db_file = db_file
        self.index_file = index_file
        self.passfile = passfile
        
        self.db = self.bkp_and_open(self.db_file, num_backups, backup_freq)
        self.retrieve_pass()

        
    def bkp_and_open(self, db_file, num_backups, backup_freq):
        """Before opening the file, check if backups need to be done"""
        #db_directory = os.path.dirname(db_file)
        NEED_BACKUP = False
        
        today = datetime.today()
        bkp_basename = db_file + '_bkp' # all bkp files are this + date string
        bkp_files = glob.glob(bkp_basename + '*')
        

        bkp_dates = [datetime.strptime(filename.split(bkp_basename)[1], bkp_dateformat)
                     for filename in bkp_files]
        bkp_distances = [(today-date).days for date in bkp_dates]

        if len(bkp_files) == 0:
            NEED_BACKUP = True

        else:
            # is it time for a fresh backup?
            if min(bkp_distances) >= backup_freq:
                NEED_BACKUP = True


        if NEED_BACKUP:
            new_bkpfilename = bkp_basename + today.strftime(bkp_dateformat)
            shutil.copy(db_file, new_bkpfilename)
            bkp_files.append(new_bkpfilename)

        if len(bkp_files) > num_backups: 
            oldest_file = bkp_files[bkp_distances.index(max(bkp_distances))]
            os.remove(oldest_file)
                            
        db = shelve.open(db_file)

        return db


    def retrieve_pass(self):
        """If the db has a stored password hash, retrieve it.
        else create a new password as a blank string"""
        try:
            #self.passhash = self.db['passhash']
            self.passhash = open(self.passfile).read()
        except KeyError:
            print 'password file missing'
            sys.exit(1)
            # md5 hash for blank string
            # self.passhash = 'd41d8cd98f00b204e9800998ecf8427e'
            # self.db['passhash'] = 'd41d8cd98f00b204e9800998ecf8427e'
            # self.db.sync()

    
    def create_index(self, restrict_ids=None):
        """index is a list of tuples
        corresponding to the values in index file.
        Convert into a dictionary to allow sorting in the
        listctrl.
        restrict_ids is a list of ids to restrict to
        The keys for index have to be integers to allow
        sorting in the listctrl"""
        # TODO: Dont read from the file each time
        fi = open(self.index_file)
        self.index_fields = yaml.load(fi)['register_keys']
        if restrict_ids == None:
            restrict_ids = self.db.keys()

        index = {}
        for id in restrict_ids:
            index[int(id)] = [self.db[id].get(field, '') for field in self.index_fields]

        # for now read the qrcode fields here
        with open(self.index_file) as fi:
            self.qrcode_fields = yaml.load(fi)['qrcode']
        
        return index


    def get_field_rec(self, rec, field):
        """from self.db, get the value of the field
        for the rec. If they field is not present,
        return empty string"""
        try:
            return self.db[rec][field]
        except KeyError:
            return ''
    

    def insert_record(self, record, unique_id=None):
        """Insert a record into the database.
        If id is given, the record is being modified"""
        if unique_id:
            del self.db[unique_id]

        else:
            unique_id = self.generate_new_id()
        
        # insert this record
        self.db[unique_id] = record
        self.db.sync() #sync immediately


    def generate_new_id(self):
        """
        Generate a new unique id for a new entry in the db.
        ids have to be strings, but they are string form
        of ints making them easier to track
        """
        return str(max([int(x) for x in self.db.keys()])+1)
        

    def retrieve_record(self, unique_id):
        """Get the specified record"""
        return self.db[unique_id]
    
        
    def delete_record(self, unique_id):
        """Delete record corresponding to record_id"""
        del self.db[unique_id]
        self.db.sync()

        
    def to_csv(self, fields, filename):
        """export the database to a csv file.
        fields is a tuple of header corresponding
        to the dictionary keys"""
        # string format for each row
        row_format = '%s,' * len(fields) + '\n'

        with open(filename, 'w') as f:
            # header row
            f.write(row_format % fields)
            # record per row
            for record in self.db:
                f.write(row_format % tuple([self.db[record][key]
                                            for key in fields]))

    def retrieve_column(self, fieldname):
        """Retrieve the values corresponding to
        a single key for all the records"""
        return [self.db[record][fieldname] for record in self.db]


    def retrieve_column_with_id(self, fieldname):
        """Like retrieve_column, but also return
        id corresponding to each element"""
        if fieldname == 'Anywhere':
            return [(''.join([str(val) for val in self.db[id].values()]), id)
                    for id in self.db]
        else:
            return [(self.db[id][fieldname], id) for id in self.db]
                


def test():
    """test and demo"""
    testdb = 'test/test.db'
    testindex = 'test/index.yaml'

    rec = Records(testdb, testindex)

    print rec.index


def test_bkp():
    testdb = '/data/tmp/test.db'
    r = Records(testdb, '', 3, 1)
    db = r.bkp_and_open(testdb, 3, 1)
    

def create_index(records, restrict_ids, index_fields):
    """records is a dict.
    Create a smaller dict index
    that contains only keys in restrict_ids
    and only fields in index_fields
    """
    index_parts = []

    for field in index_fields:
        index_parts.append([records[rec][field] for rec in records
                             if rec in restrict_ids])

    index = zip(*index_parts)

    index_dict = {}
    for i, rec in enumerate(index):
        index_dict[i] = rec

    return index_dict


def create_index2(records, restrict_ids, index_fields):
    """
    Create index as above. But use the same key for the index
    """
    print index_fields
    index = {}
    for id in restrict_ids:
        index[id] = [records[id][field] for field in index_fields]
        # for field in records[id]:
        #     if field in index_fields:
        #         index[id][field] = records[id][field]

    return index
    

def test_create_index():
    """Test for the function
    create_index"""
    records = {1:{'Name':'John', 'Age':35, 'Sex':'Male'},
               2:{'Name':'Jane', 'Age':36, 'Sex':'Female'},
               3:{'Name':'Johnny', 'Age':13, 'Sex':'Male'},
               4:{'Name':'Joan', 'Age':25, 'Sex':'Female'}}
    restrict_ids = [2, 3]
    index_fields = ['Name', 'Age']

    print create_index2(records, restrict_ids, index_fields)
    
    
def create_testdb():
    """create a db for testing"""
    test_data = {
    'Raja38':{'Demographics_Name':'Raja', 'Demographics_Age':38, 'Demographics_Sex':'Male',
                  'Demographics_Date':'20-04-2010'},
   'Rajesh30':{'Demographics_Name':'Rajesh', 'Demographics_Age':30, 'Demographics_Sex':'Male',
                  'Demographics_Date':'19-02-2010' }}

    dbfile = 'test/records.db'
    db = shelve.open(dbfile)

    for key in test_data:
        db[key] = test_data[key]

    db.close()

if __name__ == '__main__':
    #test()
    #create_testdb()
    import time
    stime = time.time()
    #for t in range(10000):
    print test_create_index()
    print time.time() - stime
        
