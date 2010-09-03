#!/usr/bin/env python

# Author: Raja Selvaraj <rajajs@gmail.com>
# License: GPL

import wx
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin, ColumnSorterMixin

import os
import sys
import glob
import subprocess

from records import Records
from form import Form
from report import Report

ID_NEW = wx.NewId()
ID_EDIT = wx.NewId()
ID_REMOVE = wx.NewId()
ID_PREF = wx.NewId()
ID_QUIT = wx.NewId()



class ReportManager():
    """The primary controller.
    Manages one 'project' at a time.
    Coordinates the form for input, records for storage and report for generating output"""
    def __init__(self):
        self.load_project()

        self.records = Records(self.db_file, self.index_file)
        self.register = Register(self, self.records)

    def load_project(self):
        """User selects a project"""
        dlg = wx.DirDialog(None, "Choose project directory")
        if dlg.ShowModal() == wx.ID_OK:
            self.project_dir = dlg.GetPath()

        # paths
        self.fields_file = os.path.join(self.project_dir, 'fields.yaml')
        self.index_file = os.path.join(self.project_dir, 'index.yaml')
        self.report_files = glob.glob(os.path.join(self.project_dir, '*.rst'))
        self.db_file = os.path.join(self.project_dir, 'records.db')
        self.all_stylefile = os.path.join(self.project_dir, 'all.sty')
        
        # verify
        VALID_PROJ = True
        missing_files = []

        if not os.path.exists(self.fields_file):
            VALID_PROJ = False
            missing_files.append('Fields file')

        if not os.path.exists(self.index_file):
            VALID_PROJ = False
            missing_files.append('Index file')

        if len(self.report_files) == 0:
            VALID_PROJ = False
            missing_files.append('Report_Files')

        if not VALID_PROJ:
            print 'Not all files required for project are present. The following files are missing'
            for f in missing_files:
                print f
            print 'exiting ...'
            sys.exit()


    def new_record(self, event):
        """Insert new record.
        Get values by presenting an empty form"""
        form = Form(None, self.fields_file, 'Fill in the values')
        if form.ShowModal() == wx.ID_OK:
            form.get_values()
            self.records.insert_record(form.vals)
            self.register.refresh_records()
            
        form.Destroy()


    def edit_record(self, event):
        """Load the selected record into a form for editing."""
        selected_record = self.register.record_display.GetFirstSelected()

        if selected_record == -1:
            print 'No record selected'
            return

        id = str(''.join([self.register.record_display.GetItem(
                        selected_record, x).GetText()
                        for x in range(len(self.records.index_keys))]))

        record_vals = self.records.retrieve_record(id)

        form = Form(None, self.fields_file, 'Edit the values', record_vals)

        if form.ShowModal() == wx.ID_OK:
            form.get_values()
            # delete the prev record
            self.records.delete_record(id)
            self.records.insert_record(form.vals)
            self.register.refresh_records()

        form.Destroy()
        

    def generate_report(self, event):
        """Generate report for the selected record in the register
        using the specified report"""
        #TODO: check for raw_report
        
        selected_record = self.register.record_display.GetFirstSelected()

        if selected_record == -1:
            print 'No record selected'
            return

        # convert to string coz unicode object does not work
        id = str(''.join([self.register.record_display.GetItem(
                    selected_record, x).GetText()
                    for x in range(len(self.records.index_keys))]))
        
        template_file = self.report_files[event.Id]
        record_vals = self.records.retrieve_record(id)

        # style file in the project directory
        # same name as report or all.sty
        stylefile = os.path.splitext(template_file)[0] + '.sty'
        if os.path.exists(stylefile):
            rep = Report(template_file, record_vals, '', stylefile)
        else:
            rep = Report(template_file, record_vals)
        
        pdf_file = rep.generate_pdf()
        self.display_pdf(pdf_file)


    def display_pdf(self, pdf_file):
        """Display the pdf using the native viewer"""
        if sys.platform.startswith('linux'):
            subprocess.Popen('evince', pdf_file)

        elif sys.platform == 'win32':
            os.startfile(pdf_file)

        # elif sys.platform == 'darwin':
        #     return 'mac'
        

class Register(wx.Frame):
    """Display the index and allow selection and operation on records"""
    def __init__(self, parent, records):
        """records is a Records instance - provides the db functions"""
        wx.Frame.__init__(self, None, -1, 'Report Manager', size=(460,600))

        self.parent = parent
        self.records = records
        
        self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.vbox = wx.BoxSizer(wx.VERTICAL)
        
        panel = wx.Panel(self, -1)
        
        # listcontrol
        self.record_display = AutoWidthListCtrl(panel)

        # buttons
        self.edit_button = wx.Button(panel, -1,  'Edit Record')
        self.new_button = wx.Button(panel, -1, 'New Record')
        self.remove_button = wx.Button(panel, -1, 'Remove Record')
        
        self.hbox1.Add(self.record_display, 1, wx.ALL|wx.EXPAND, 10)
        self.hbox2.Add(self.new_button, 1, wx.ALL, 5)
        self.hbox2.Add(self.edit_button, 1, wx.ALL, 5)
        self.hbox2.Add(self.remove_button, 1, wx.ALL, 5)
        
        self.vbox.Add(self.hbox1, 6, wx.EXPAND, 10)
        self.vbox.Add(self.hbox2, 1, wx.ALL, 10)

        self._build_menubar()
        self._set_bindings()

        panel.SetSizer(self.vbox)
        self.Centre()
        self.Show(True)

        self.load_records()

    def _build_menubar(self):
        """Build the menu bar"""
        self.MenuBar = wx.MenuBar()

        file_menu = wx.Menu()
        file_menu.Append(ID_NEW, "&New Record","Create a new record")
        file_menu.Append(ID_EDIT, "&Edit Record", "Edit an existing record")
        file_menu.Append(ID_REMOVE, "&Remove Record", "Remove existing record")
        file_menu.Append(ID_QUIT, "&Quit","Quit the program")
   
        edit_menu = wx.Menu()
        edit_menu.Append(ID_PREF, "Preferences", "Edit preferences")

        report_gen_menu = wx.Menu()
        for i in range(len(self.parent.report_files)):
            report_name = os.path.basename(self.parent.report_files[i]).rstrip('.rst')
            report_gen_menu.Append(i, report_name)
        
        self.MenuBar.Append(file_menu, "&File")
        self.MenuBar.Append(report_gen_menu, "&Generate Report")
        self.MenuBar.Append(edit_menu, "&Edit")
        
        
        self.SetMenuBar(self.MenuBar)

    def _set_bindings(self):
        """All the bindings"""
        self.Bind(wx.EVT_CLOSE, self.on_quit)
        self.new_button.Bind(wx.EVT_BUTTON, self.parent.new_record)
        self.edit_button.Bind(wx.EVT_BUTTON, self.parent.edit_record)
        self.remove_button.Bind(wx.EVT_BUTTON, self.remove_record)
        
        self.Bind(wx.EVT_MENU, self.parent.new_record, id=ID_NEW)
        self.Bind(wx.EVT_MENU, self.parent.edit_record, id=ID_EDIT)
        self.Bind(wx.EVT_MENU, self.on_quit, id=ID_QUIT)

        # all generate report events are bound to one function
        for i in range(len(self.parent.report_files)):
            self.Bind(wx.EVT_MENU, self.parent.generate_report, id=i)

    def load_records(self):
        """Load the index and display"""
        summary = self.records.create_index()
        
        # for sorting we use the full db
        # itemdatamap must be a dict
        self.record_display.itemDataMap = summary

        index_keys = self.records.index_keys
        
        # create the columns
        for i, val in enumerate(index_keys):
            keyname = val.split('_')[1]
            self.record_display.InsertColumn(i, keyname)
        
        #self.record_display.ClearAll()
        for key in summary:
            self.record_display_append(summary[key], key)


    def refresh_records(self):
        """Completely refresh the summary being shown"""
        self.record_display.ClearAll()
        self.load_records()

    def record_display_append(self, rec, key):
        """add the rec to display"""
        # convert everything to a string
        rec = [str(x) for x in rec]
        
        id = self.record_display.InsertStringItem(sys.maxint, rec[0])

        for col in range(1, len(rec)):
            self.record_display.SetStringItem(id, col, rec[col])

        self.record_display.SetItemData(id, key) 
            
        
    def on_quit(self, event):
        """Things to do on exiting"""
        self.records.db.close()
        sys.exit()

        
    # def load_and_edit_record(self):
    #     pass

    def remove_record(self):
        pass
        
        

class AutoWidthListCtrl(wx.ListCtrl, ListCtrlAutoWidthMixin, ColumnSorterMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT)
        ListCtrlAutoWidthMixin.__init__(self)
        ColumnSorterMixin.__init__(self, 4)

    def GetListCtrl(self):
        return self

        
            

        
class Reporter(wx.Frame):

        
    def load_and_edit_record(self, event):
        """Load the selected record into a form for editing"""
        selected_record = self.record_display.GetFirstSelected()

        if selected_record == -1: # none selected
            return

        # convert to string coz unicode object does not work
        selected_record_key = str(''.join([self.record_display.GetItem(
                    selected_record, x).GetText()
                    for x in range(len(self.index_keys))]))

        rec = self.db.db[selected_record_key]
        f = Form(Non, 'report_docs/form_fields.yaml', selected_record_key)
        f.set_values(rec)


    def remove_record(self, event):
        """Remove selected record from the database"""
        selected_record = self.record_display.GetFirstSelected()
        if selected_record == -1: # none selected
            return

        # TODO: separate function to get key
        selected_record_key = str(''.join([self.record_display.GetItem(
                    selected_record, x).GetText()
                    for x in range(len(self.index_keys))]))

        self.db.delete_record(selected_record_key)


    def render_report(self, event):
        """Render selected record as a pdf"""
        #TODO: refactor to avoid repetition
        selected_record = self.record_display.GetFirstSelected()
        if selected_record == -1: # none selected
            return

        # convert to string coz unicode object does not work
        id = str(''.join([self.record_display.GetItem(
                    selected_record, x).GetText()
                    for x in range(len(self.index_keys))]))

        #id = str(self.record_display.GetItem(selected_record, 0).GetText())

        rec = self.db.db[id]

        report_template = Template(filename='report_docs/ep_report_template.rst')
        rep = report_template.render(vals = rec)

        reportfile = 'report_docs/report.rst'
        with open(reportfile, 'w') as fi:
            fi.write(rep)
        self.write_pdf(rep)
        

    def record_display_append(self, rec, key):
        """add the rec to display"""
        index = self.record_display.InsertStringItem(sys.maxint, rec[0])
        self.record_display.SetStringItem(index, 1, str(rec[1]))
        self.record_display.SetStringItem(index, 2, rec[2])
        self.record_display.SetStringItem(index, 3, rec[3])
        #self.record_display.SetStringItem(index, 4, rec[4])
        self.record_display.SetItemData(index, key) 
            
    def update_record(self, id):
        """Update the record with given id"""
        self.db.db[id] = self.record


def test():
    app= wx.App()
    rm = ReportManager()
    app.MainLoop()

if __name__ == '__main__':
    test()    
