#!/usr/bin/env python

import os
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
    def __init__(self, db_file, index_file, num_backups, backup_freq):
        self.db_file = db_file
        self.index_file = index_file

        #self.db = self.bkp_and_open(self.db_file, num_backups, backup_freq)
        self.db = shelve.open(self.db_file)

    def bkp_and_open(self, db_file, num_backups, backup_freq):
        """Before opening the file, check if backups need to be done"""
        #db_directory = os.path.dirname(db_file)
        NEED_BACKUP = False
        
        today = datetime.today()
        bkp_basename = db_file + '_bkp' # all bkp files are this + date string
        bkp_files = glob.glob(bkp_basename + '*')
        bkp_dates = [datetime.strptime(filename.lstrip(bkp_basename), bkp_dateformat)
                     for filename in bkp_files]
        bkp_distances = [(today-date).days for date in bkp_dates]

        if len(bkp_files) == 0:
            NEED_BACKUP = True

        else:
            if max(bkp_distances) >= backup_freq:
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
        
    def create_index(self, restrict_ids=None):
        """index is a list of tuples
        corresponding to the values in index file.
        Convert into a dictionary to allow sorting in the
        listctrl.
        restrict_ids is a list of ids to restrict to"""
        self.index_keys = yaml.load(open(self.index_file))
        index_fields = []

        if restrict_ids == None:
            restrict_ids = self.db.keys()

        for field in self.index_keys:
            index_fields.append([self.db[rec][field] for rec in self.db if rec in restrict_ids])

        index = zip(*index_fields)

        index_dict = {}
        for i, rec in enumerate(index):
            #rec_key = str(''.join([str(x) for x in rec]))
            index_dict[i] = rec

        return index_dict


    def insert_record(self, record):
        """Insert a record into the database.
        The key for each record is a unique id
        constructed by joining all the index elements.
        record is a dict
        eg: {'Name': 'Raja', 'Age': 39}"""
        unique_id = ''.join([str(record[k]) for k in self.index_keys])
        
        # insert this record
        self.db[unique_id] = record
        self.db.sync() #sync immediately


    def retrieve_record(self, unique_id):
        """Get the specified record"""
        return self.db[unique_id]
    
        
    def delete_record(self, unique_id):
        """Delete record corresponsing to record_id"""
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
    test_bkp()
