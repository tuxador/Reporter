"""The main controller for the reports.
On the one hand it interfaces with the database
to retrieve old records and store new ones.
On the other hand it interfaces with the form to
collect information to insert in a new record"""

#import os
import sys
import wx
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin, ColumnSorterMixin
import shelve
from form import Form
    
class ReportDatabase():
    def __init__(self, db_path):
        """db_path is full path to the database"""
        self.db_path = db_path
        self.db = shelve.open(db_path)        

    def get_index(self, index_fields):
        """Get data from db to create an index.
        index_fields are the fields for creating the index
        return list of tuples"""
        index_field_vals = []
        for field in index_fields: 
            index_field_vals.append([self.db[str(x)][field]
                                     for x in range(len(self.db))])
            
        vals = zip(*index_field_vals)

        record_summary = {}
        for i in range(len(vals)):
            record_summary[i] = vals[i]

        return record_summary

    
    def insert_record(self, record_dict):
        """Insert a record into the database.
        record_dict is a dict
        eg: {'Name': 'Raja', 'Age': 39}"""
        # find last id
        try:
            last_id = max([int(x) for x in self.db.keys()])
        except ValueError: # empty dict
            last_id = -1

        # insert this record
        self.db[str(last_id+1)] = record_dict


    def delete_record(self, rec_id):
        """Delete record corresponsing to record_id"""
        del self.db[rec_id]

    def dump(self):
        """dump all the database records"""
        for rec in self.db: 
            print rec


            
class AutoWidthListCtrl(wx.ListCtrl, ListCtrlAutoWidthMixin, ColumnSorterMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT)
        ListCtrlAutoWidthMixin.__init__(self)
        ColumnSorterMixin.__init__(self, 4)

    def GetListCtrl(self):
        return self

        
            
class Reporter(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, size=(400, 600))

        self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.vbox = wx.BoxSizer(wx.VERTICAL)
        
        panel = wx.Panel(self, -1)

        # listcontrol
        self.record_display = AutoWidthListCtrl(panel)
        self.record_display.InsertColumn(0, 'Name', width=120)
        self.record_display.InsertColumn(1, 'Age', width=30)
        self.record_display.InsertColumn(2, 'Sex', width=60)
        self.record_display.InsertColumn(3, 'Procedure Date', 100)

        # buttons
        self.view_button = wx.Button(panel, -1, 'View Record')
        self.edit_button = wx.Button(panel, -1,  'Edit Record')
        self.new_button = wx.Button(panel, -1, 'New Record')

        self.new_button.Bind(wx.EVT_BUTTON, self.new_record)

        
        self.hbox1.Add(self.record_display, 1, wx.ALL|wx.EXPAND, 10)
        self.hbox2.Add(self.view_button, 1, wx.ALL, 10)
        self.hbox2.Add(self.edit_button, 1, wx.ALL, 10)
        self.hbox2.Add(self.new_button, 1, wx.ALL, 10)
        
        self.vbox.Add(self.hbox1, 5, wx.EXPAND, 5)
        self.vbox.Add(self.hbox2, 1, wx.ALL, 5)

        # instantiate the db
        self.db = ReportDatabase('/data/tmp/testdb')
        self.rec_summary = self.db.get_index(
            ('Demographics_Name', 'Demographics_Age',
             'Demographics_Sex', 'Demographics_Date of Procedure'))

        self.show_records(self.rec_summary)
        self.record = {} #active record in memory

        panel.SetSizer(self.vbox)
        self.Centre()
        self.Show(True)
        
    def show_records(self, records):
        """Populate the listctrl with record summaries.
        records is a list of tuples"""
        self.record_display.itemDataMap = records

        #self.record_display.ClearAll()
        for ind in range(len(records)):
            rec = records[ind]
            self.record_display_append(rec, ind)


    def record_display_append(self, rec, ind):
        """add the rec to display"""
        index = self.record_display.InsertStringItem(sys.maxint, rec[0])
        self.record_display.SetStringItem(index, 1, str(rec[1]))
        self.record_display.SetStringItem(index, 2, rec[2])
        self.record_display.SetStringItem(index, 3, rec[3])
        self.record_display.SetItemData(index, ind)
            
            
    def new_record(self, event):
        """Create a new record"""
        f = Form(self, 'report_docs/form_fields.yaml')

    def insert_record(self):
        """Insert the record into the database.
        Will be triggered from the form"""
        self.db.insert_record(self.record)

        #self.record_display.ClearAll()
        #TODO: just append to rec_summary
        rec_summary = [self.record[k] for k in ['Demographics_Name',
                      'Demographics_Age', 'Demographics_Sex',
                      'Demographics_Date of Procedure']]
        self.record_display_append(rec_summary, len(self.rec_summary))
        #self.show_records()
        #self.db.close()

        
def db_tests(path):
    """Create a db in the path, and test it"""
    print 'Creating db'
    manager = ReportDatabase(path)
 
    print 'insert record'
    reca = {'Name': 'Raja', 'Age': 38, 'Sex':'M'}
    recb = {'Name': 'Rajan', 'Age': 39, 'Sex':'M'}
    recc = {'Name': 'Rajee', 'Age': 48, 'Sex':'F'}

    manager.insert_record(reca)
    manager.insert_record(recb)
    manager.insert_record(recc)

    # debug
    print manager.db.ids()
    
    print 'get index'
    print manager.get_index(('Name', 'Age'))

    print 'dump data'
    print manager.dump()


if __name__ == '__main__':
    app = wx.App()
    rep = Reporter(None, -1, 'Records')
    app.MainLoop()

    
