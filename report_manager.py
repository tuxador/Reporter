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
from config_manager import Config

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
        configfile = self.get_configfile()
        self.config = Config(configfile)
        
        self.load_project()

        self.records = Records(self.db_file, self.index_file)
        self.register = Register(self, self.records, self.project_name)


    def get_configfile(self):
        """Get path to config file"""
        platform = sys.platform
        if platform.startswith('linux'):
            return os.path.expanduser('~/.reportmanagerrc')
        elif platform == 'win32':
            return 'reportmanager.conf'
        
        
    def load_project(self, project_dir = None):
        """User selects a project if project dir is not given"""
        if not project_dir:
            dlg = wx.DirDialog(None, "Choose project directory")
            if dlg.ShowModal() == wx.ID_OK:
                self.project_dir = dlg.GetPath()
            else:
                self.project_dir = project_dir
                return # TODO:

        # paths
        self.fields_file = os.path.join(self.project_dir, 'fields.yaml')
        self.index_file = os.path.join(self.project_dir, 'index.yaml')
        self.report_files = glob.glob(os.path.join(self.project_dir, '*.rst'))
        self.db_file = os.path.join(self.project_dir, 'records.db')
        self.all_stylefile = os.path.join(self.project_dir, 'all.sty')

        self.project_name = os.path.basename(self.project_dir)
        
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
        selected_record = self.register.record_display.GetFirstSelected()

        if selected_record == -1:
            print 'No record selected'
            return

        # convert to string coz unicode object does not work
        id = str(''.join([self.register.record_display.GetItem(
                    selected_record, x).GetText()
                    for x in range(len(self.records.index_keys))]))
        
        template_file = self.report_files[event.Id // 2]
        record_vals = self.records.retrieve_record(id)

        # retrieve stored raw report
        try:
            raw_report = record_vals['raw_report']
        except KeyError:
            raw_report = ''
        
        # style file in the project directory
        # same name as report or all.sty
        local_stylefile = os.path.splitext(template_file)[0] + '.sty'
        global_stylefile = os.path.join(os.path.dirname(template_file), 'all.sty')

        if os.path.exists(local_stylefile):
            rep = Report(template_file, record_vals, raw_report, local_stylefile)
        elif os.path.exists(global_stylefile):
            rep = Report(template_file, record_vals, raw_report, global_stylefile)
        else:
            rep = Report(template_file, record_vals, raw_report)
        
        pdf_file = rep.generate_pdf()
        self.display_pdf(pdf_file)


    def edit_report(self, event):
        """Display the report for the selected record and allow edits"""
        selected_record = self.register.record_display.GetFirstSelected()

        if selected_record == -1:
            print 'No record selected'
            return

        # convert to string coz unicode object does not work
        id = str(''.join([self.register.record_display.GetItem(
                    selected_record, x).GetText()
                    for x in range(len(self.records.index_keys))]))
        print id
        
        template_file = self.report_files[event.Id // 2]
        record_vals = self.records.retrieve_record(id)

        # retrieve stored raw report
        try:
            raw_report = record_vals['raw_report']
        except KeyError:
            raw_report = ''
        
        # style file in the project directory
        # same name as report or all.sty
        stylefile = os.path.splitext(template_file)[0] + '.sty'
        if os.path.exists(stylefile):
            rep = Report(template_file, record_vals, raw_report, stylefile)
        else:
            rep = Report(template_file, record_vals, raw_report)

        raw_report =  rep.edit_report()
        
        record_vals['raw_report'] = raw_report
        self.records.insert_record(record_vals)

        
    def display_pdf(self, pdf_file):
        """Display the pdf using the native viewer"""
        #print pdf_file
        if sys.platform.startswith('linux'):
            subprocess.Popen(['evince', pdf_file])

        elif sys.platform == 'win32':
            os.startfile(pdf_file)

        # elif sys.platform == 'darwin':
        #     return 'mac'
        

class Register(wx.Frame):
    """Display the index and allow selection and operation on records"""
    def __init__(self, parent, records, project_name):
        """records is a Records instance - provides the db functions"""
        wx.Frame.__init__(self, None, -1, project_name, size=(460,600))

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
        self.vbox.Add(self.hbox2, 1, wx.ALL|wx.EXPAND, 10)

        self._build_menubar()
        self._set_bindings()

        panel.SetSizer(self.vbox)

        # sizer_1.Add(self.panel_1, 1, wx.EXPAND, 0)
        # self.SetSizer(sizer_1)
        # sizer_1.Fit(self)
        # self.Layout()

        mainsizer = wx.BoxSizer(wx.HORIZONTAL)
        mainsizer.Add(panel, 1, wx.EXPAND, 5)
        mainsizer.Fit(self)
        self.Layout()
        # self.SetSizer(mainsizer)
        
        #self.Layout()
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
            report_gen_menu.Append(2*i, report_name)

        # TODO: Avoid repetition and incorporate in prev loop
        report_edit_menu = wx.Menu()
        for i in range(len(self.parent.report_files)):
            report_name = os.path.basename(self.parent.report_files[i]).rstrip('.rst')
            report_edit_menu.Append(2*i + 1, report_name)
        
        self.MenuBar.Append(file_menu, "&File")
        self.MenuBar.Append(report_gen_menu, "&Generate Report")
        self.MenuBar.Append(report_edit_menu, "&Edit Report")
        
        
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
            self.Bind(wx.EVT_MENU, self.parent.generate_report, id=2*i)

        # all edit report events
        for i in range(len(self.parent.report_files)):
            self.Bind(wx.EVT_MENU, self.parent.edit_report, id=2*i + 1)

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

        
            



def test():
    app= wx.App()
    rm = ReportManager()
    #rm.Show(True)
    app.MainLoop()

if __name__ == '__main__':
    test()    
