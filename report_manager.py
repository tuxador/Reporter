#!/usr/bin/env python

# Author: Raja Selvaraj <rajajs@gmail.com>
# License: GPL

import wx
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin, ColumnSorterMixin

import os
import sys
import glob
import subprocess
import time
import yaml


from records import Records
from form import Form
from report import Report
from config_manager import Config

ID_NEW = wx.NewId()
ID_EDIT = wx.NewId()
ID_REMOVE = wx.NewId()
ID_PREF = wx.NewId()
ID_FLUSH = wx.NewId()
ID_NEWTEMPLATE = wx.NewId()
ID_DELTEMPLATE = wx.NewId()
ID_QUIT = wx.NewId()


class ReportManager():
    """The primary controller.
    Manages one 'project' at a time.
    Coordinates the form for input, records for storage and report for generating output"""
    def __init__(self):
        configfile = self.get_configfile()
        self.config = Config(configfile)

        print configfile

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
        """load project based on options in config file"""
        # if not project_dir:
        #     dlg = wx.DirDialog(None, "Choose project directory")
        #     if dlg.ShowModal() == wx.ID_OK:
        #         self.project_dir = dlg.GetPath()
        #     else:
        #         self.project_dir = project_dir
        #         return # TODO:
        print self.config.options
        

        self.project_dir = self.config.options['projects'][int(self.config.options['default_project'])]
        
        # paths
        self.fields_file = os.path.join(self.project_dir, 'fields.yaml')
        self.index_file = os.path.join(self.project_dir, 'index.yaml')
        self.report_files = glob.glob(os.path.join(self.project_dir, '*.rst'))
        self.db_file = os.path.join(self.project_dir, 'records.db')
        self.all_stylefile = os.path.join(self.project_dir, 'all.sty')

        print self.project_dir
        print self.fields_file

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
        # does user want to fill with template ?
        template_chooser = TemplateChooser(None, self.project_dir)
        if template_chooser.ShowModal() == wx.ID_OK:
            template_name = template_chooser.chosentemplate
            template_chooser.Destroy()
        else:
            template_name = 'Empty'

        print 'template used', template_name
            
        if template_name == 'Empty':
            form = Form(None, self.fields_file, 'Fill in the values')            
        else:
            template_vals = yaml.load(open(template_name))
            form = Form(None, self.fields_file, 'Fill in the values', template_vals)

        if form.ShowModal() == wx.ID_OK:
            form.get_values()
            self.records.insert_record(form.vals)
            self.register.refresh_records()
            
        form.Destroy()


    def new_template(self, event):
        """Create a new template"""
        form = Form(None, self.fields_file, 'Fill in the values for template')
        if form.ShowModal() == wx.ID_OK:
            form.get_values()
            template_vals = form.vals
            form.Destroy()
            
            # get template name
            name_entry = wx.TextEntryDialog(None, 'Enter name for template')
            if name_entry.ShowModal() == wx.ID_OK:
                template_name = name_entry.GetValue()
                if not template_name.endswith('.tpl'):
                    template_name += '.tpl'
                template_name = os.path.join(self.project_dir, template_name)
                
            else:
                return

            # write the template
            yaml.dump(template_vals, open(template_name, 'w'))
        

    def del_template(self, event):
        """Delete an existing template"""
        template_chooser = TemplateChooser(None, self.project_dir)
        if template_chooser.ShowModal() == wx.ID_OK:
            template_name = template_chooser.chosentemplate
            template_chooser.Destroy()
        else:
            template_name = 'Empty'

        if template_name == 'Empty':
            return
        else:
            os.remove(template_name) #TODO: will raise an exception windows if file is in use

            
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
        

    # def generate_report(self, event):
    #     """Generate report for the selected record in the register
    #     using the specified report"""
    #     selected_record = self.register.record_display.GetFirstSelected()

    #     if selected_record == -1:
    #         print 'No record selected'
    #         return

    #     # convert to string coz unicode object does not work
    #     id = str(''.join([self.register.record_display.GetItem(
    #                 selected_record, x).GetText()
    #                 for x in range(len(self.records.index_keys))]))
        
    #     template_file = self.report_files[event.Id // 2]
    #     record_vals = self.records.retrieve_record(id)

    #     # retrieve stored raw report
    #     try:
    #         raw_report = record_vals['raw_report']
    #     except KeyError:
    #         raw_report = ''
        
    #     # style file in the project directory
    #     # same name as report or all.sty
    #     local_stylefile = os.path.splitext(template_file)[0] + '.sty'
    #     global_stylefile = os.path.join(os.path.dirname(template_file), 'all.sty')

    #     if os.path.exists(local_stylefile):
    #         rep = Report(template_file, record_vals, raw_report, local_stylefile)
    #     elif os.path.exists(global_stylefile):
    #         rep = Report(template_file, record_vals, raw_report, global_stylefile)
    #     else:
    #         rep = Report(template_file, record_vals, raw_report)

    #     pdf_file = rep.generate_pdf()
        
    #     self.display_pdf(pdf_file)



    def flush_report(self, event):
        """Remove the stored raw report for the record if it exists"""
        selected_record = self.register.record_display.GetFirstSelected()

        if selected_record == -1:
            print 'No record selected'
            return

        id = str(''.join([self.register.record_display.GetItem(
                    selected_record, x).GetText()
                    for x in range(len(self.records.index_keys))]))
        
        #template_file = self.report_files[event.Id // 2]
        #record_vals = self.records.retrieve_record(id)
        record_vals = self.records.retrieve_record(id)

        record_vals['raw_report'] = ''
        #form = Form(None, self.fields_file, 'Edit the values', record_vals)

        self.records.delete_record(id)
        self.records.insert_record(record_vals)
        #self.register.refresh_records()

        
    def show_n_edit_report(self, event):
        """Display the report for the selected record and allow edits"""
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

        raw_report =  rep.edit_report()
        
        record_vals['raw_report'] = raw_report
        self.records.insert_record(record_vals)

        
    def display_pdf(self, pdf_file):
        """Display the pdf using the native viewer"""
        print pdf_file
        if sys.platform.startswith('linux'):
            time.sleep(2)
            subprocess.Popen(['evince', pdf_file])

        elif sys.platform == 'win32':
            os.startfile(pdf_file)

        # elif sys.platform == 'darwin':
        #     return 'mac'


class TemplateChooser(wx.Dialog):
    """List the available templates and allow user to choose one"""
    def __init__(self, parent, project_dir):
        wx.Dialog.__init__(self, parent, -1, 'Choose template to use')

        self.project_dir = project_dir
        self.templates = self.get_templates(project_dir)

        # Default is empty
        self.chosentemplate = 'Empty'
        
        panel  = wx.Panel(self, -1)
        panelsizer = wx.BoxSizer(wx.VERTICAL)
        buttonsizer = wx.BoxSizer(wx.HORIZONTAL)

        self.choices = wx.RadioBox(panel, -1, "Choose template",
                                   choices=self.templates, style=wx.RA_VERTICAL)
        self.cancel_button = wx.Button(panel, -1, 'Cancel')
        self.done_button = wx.Button(panel, -1, 'Done')

        self.cancel_button.Bind(wx.EVT_BUTTON, self.cancel)
        self.done_button.Bind(wx.EVT_BUTTON, self.ondone)

        buttonsizer.Add(self.cancel_button, 0, wx.ALL, 10)
        buttonsizer.Add(self.done_button, 0, wx.ALL, 10)

        panelsizer.Add(self.choices, 10, wx.ALL|wx.EXPAND, 2)
        panelsizer.Add(buttonsizer, 1, wx.ALL, 2)
        
        panel.SetSizer(panelsizer)
        self.Layout()

        
    def _filename2templatename(self, name):
        """from filename, get the template name"""
        return os.path.basename(name)[:-4]

    
    def _templatename2filename(self, name):
        """from template name, get full filename"""
        return os.path.join(self.project_dir, name + '.tpl')
    
        
    def get_templates(self, project_dir):
        """collect template names"""
        tpl_files = glob.glob(os.path.join(project_dir, '*.tpl'))
        return [self._filename2templatename(filename) for filename in tpl_files]


    def cancel(self, event):
        """Cancel and discard edits"""
        self.EndModal(wx.ID_CANCEL)

    def ondone(self, event):
        """returns the filename to the template file"""
        self.chosentemplate = self._templatename2filename(
                              self.choices.GetStringSelection())
        self.EndModal(wx.ID_OK)


    
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
        file_menu.Append(ID_FLUSH, "&Flush report", "Remove stored report")
        file_menu.Append(ID_QUIT, "&Quit","Quit the program")
   
        edit_menu = wx.Menu()
        edit_menu.Append(ID_PREF, "Preferences", "Edit preferences")

        report_gen_menu = wx.Menu()
        for i in range(len(self.parent.report_files)):
            report_name = os.path.basename(self.parent.report_files[i]).rstrip('.rst')
            report_gen_menu.Append(2*i, report_name)


        template_menu = wx.Menu()
        template_menu.Append(ID_NEWTEMPLATE, "&New Template", "Create a new template")
        template_menu.Append(ID_DELTEMPLATE, "&Delete Template", "Delete a template")
            
        # # TODO: Avoid repetition and incorporate in prev loop
        # report_edit_menu = wx.Menu()
        # for i in range(len(self.parent.report_files)):
        #     report_name = os.path.basename(self.parent.report_files[i]).rstrip('.rst')
        #     report_edit_menu.Append(2*i + 1, report_name)
        
        self.MenuBar.Append(file_menu, "&File")
        self.MenuBar.Append(report_gen_menu, "&Generate Report")
        #self.MenuBar.Append(report_edit_menu, "&Edit Report")
        self.MenuBar.Append(template_menu, "&Template")
        
        self.SetMenuBar(self.MenuBar)

        
    def _set_bindings(self):
        """All the bindings"""
        self.Bind(wx.EVT_CLOSE, self.on_quit)
        self.new_button.Bind(wx.EVT_BUTTON, self.parent.new_record)
        self.edit_button.Bind(wx.EVT_BUTTON, self.parent.edit_record)
        self.remove_button.Bind(wx.EVT_BUTTON, self.remove_record)
        
        self.Bind(wx.EVT_MENU, self.parent.new_record, id=ID_NEW)
        self.Bind(wx.EVT_MENU, self.parent.edit_record, id=ID_EDIT)
        self.Bind(wx.EVT_MENU, self.parent.flush_report, id=ID_FLUSH)
        self.Bind(wx.EVT_MENU, self.parent.new_template, id=ID_NEWTEMPLATE)
        self.Bind(wx.EVT_MENU, self.parent.del_template, id=ID_DELTEMPLATE)
        self.Bind(wx.EVT_MENU, self.on_quit, id=ID_QUIT)

        # all generate report events are bound to one function
        for i in range(len(self.parent.report_files)):
            self.Bind(wx.EVT_MENU, self.parent.show_n_edit_report, id=2*i)

        # # all edit report events
        # for i in range(len(self.parent.report_files)):
        #     self.Bind(wx.EVT_MENU, self.parent.show_n_edit_report, id=2*i + 1)

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
