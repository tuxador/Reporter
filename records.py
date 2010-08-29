#!/usr/bin/env python


import shelve
import yaml

class Records():
    """Database functions"""
    def __init__(self, db_file, index_file):
        self.db_file = db_file
        self.index_file = index_file

        self.db = shelve.open(self.db_file)
        #self.index_keys = yaml.load(open(index_file))

        #self.create_index() # init self.index

        
    def create_index(self):
        """index is a list of tuples
        corresponding to the values in index file.
        Convert into a dictionary to allow sorting in the
        listctrl"""
        self.index_keys = yaml.load(open(self.index_file))
        index_fields = []

        for field in self.index_keys:
            index_fields.append([self.db[rec][field] for rec in self.db])

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


    def retrieve_record(self, unique_id):
        """Get the specified record"""
        return self.db[unique_id]
    
        
    def delete_record(self, unique_id):
        """Delete record corresponsing to record_id"""
        del self.db[unique_id]

        
    def to_csv(self, fields, filename):
        """export the database to a csv file.
        fields is a tuple of header corresponding
        to the dictionary keys"""
        # string format for each row
        row_format = '%s,' * len(fields) + '\n'

        print 'fields', fields
        with open(filename, 'w') as f:
            # header row
            f.write(row_format % fields)
            # record per row
            for record in self.db:
                f.write(row_format % tuple([self.db[record][key]
                                            for key in fields]))
            


def test():
    """test and demo"""
    testdb = 'test/test.db'
    testindex = 'test/index.yaml'

    rec = Records(testdb, testindex)

    print rec.index
    
def create_testdb():
    """create a db for testing"""
    test_data = {
    'uniq_hash1':{'Demographics_Name':'Raja', 'Demographics_Age':38, 'Demographics_Sex':'Male',
                  'Demographics_Date':'20-04-2010'},
   'uniq_hash2':{'Demographics_Name':'Rajesh', 'Demographics_Age':30, 'Demographics_Sex':'Male',
                  'Demographics_Date':'19-02-2010' }}

    dbfile = 'test/records.db'
    db = shelve.open(dbfile)

    for key in test_data:
        db[key] = test_data[key]

    db.close()

if __name__ == '__main__':
    test()
    #create_testdb()
