#!/usr/bin/env python

# Author: Raja Selvaraj <rajajs@gmail.com>
# License: GPL
import wx
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin, ColumnSorterMixin, ListRowHighlighter

import os
import sys
import glob
import subprocess
import time
import yaml
import hashlib
import csv
#import numpy

from records import Records
from form import Form
from read_only_form import ReadOnlyForm
from report import Report
from config_manager import Config
from summary import NumSummary, CatSummary

ID_NEW = wx.NewId()
ID_EDIT = wx.NewId()
ID_LOCK = wx.NewId()
ID_REMOVE = wx.NewId()
ID_PREF = wx.NewId()
ID_FLUSH = wx.NewId()
ID_NEWTEMPLATE = wx.NewId()
ID_DELTEMPLATE = wx.NewId()
ID_QUIT = wx.NewId()
ID_NUM_SUMMARY = wx.NewId()
ID_CAT_SUMMARY = wx.NewId()
ID_PASS = wx.NewId()
ID_PROJ = wx.NewId()
ID_EXPORT = wx.NewId()
ID_RECEXPORT = wx.NewId()

#----------------------------
# Utility functions

def str2float(s):
    """Convert the string s to a float.
    If empty string or invalid literal,
    return empty string"""
    try:
        return float(s)
    except ValueError, AttributeError:
        return ''


def meanstdv(x): 
    """ Calculate mean and standard deviation of data x[]: 
    mean = {\sum_i x_i \over n} 
    std = sqrt(\sum_i (x_i - mean)^2 \over n-1) """ 

    from math import sqrt 
    n, mean, std = len(x), 0, 0 
    for a in x: 
        mean = mean + a 
    mean = mean / float(n) 
    for a in x: 
        std = std + (a - mean)**2 
    std = sqrt(std / float(n-1)) 
    return mean, std


#-----------------------------
class ReportManager():
    """The primary controller.
    Manages one 'project' at a time.
    Coordinates the form for input, records for storage and report for generating output"""
    def __init__(self):
        # if 'new.txt' exists, show it in a dialog
        if os.path.exists('new.txt'):
            msg = open('new.txt').read()
            new_dlg = WhatsNew(self, msg)
            if new_dlg.ShowModal() == wx.ID_CANCEL:
                os.remove('new.txt')
            else:
                pass
                
        
        configfile = self.get_configfile()
        self.config = Config(configfile)
        self.init_project()


    def init_project(self):
        """Common code for initialising project"""
        self.load_project()

        self.records = Records(self.db_file, self.index_file, self.passfile,
                               self.config.options['num_backups'],
                               self.config.options['backup_freq'])
        self.register = Register(self, self.records, self.project_name)
        

    def unload_current_project(self):
        """Close cleanly current loaded project"""
        self.register.Destroy()
        
        
    def get_configfile(self):
        """Get path to config file"""
        platform = sys.platform
        if platform.startswith('linux'):
            return os.path.expanduser('~/.reportmanagerrc')
        elif platform == 'win32':
            return 'reportmanager.conf'
        
        
    def load_project(self, project_dir = None):
        """load project based on options in config file"""
        self.project_dir = self.config.options['projects'][
            int(self.config.options['default_project'])]
   
        # paths
        self.fields_file = os.path.join(self.project_dir, 'fields.yaml')
        self.index_file = os.path.join(self.project_dir, 'index.yaml')
        self.report_files = glob.glob(os.path.join(self.project_dir, '*.rst'))
        self.db_file = os.path.join(self.project_dir, 'records.db')
        self.all_stylefile = os.path.join(self.project_dir, 'all.sty')
        self.passfile = os.path.join(self.project_dir, 'pass.hsh')

        # images (including logo) will all be stored in an image folder.
        self.image_folder = os.path.join(self.project_dir, 'images')
        
        self.tpl_files = glob.glob(os.path.join(self.project_dir, '*.tpl'))
        
        self.project_name = os.path.basename(self.project_dir)
        
        # verify
        VALID_PROJ = True
        missing_files = []

        if not os.path.exists(self.fields_file):
            print 'missing fields', self.fields_file
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


    def change_project(self, event):
        """Load a new project"""
        project_chooser = ProjectChooser(None, self.config)
        if project_chooser.ShowModal() == wx.ID_OK:
            chosen_project = project_chooser.default_project
            self.config.options['default_project'] = chosen_project
            project_chooser.Destroy()

        self.unload_current_project()
        self.init_project()

            
    def new_record(self, event):
        """Insert new record.
        Get values by presenting an empty form"""
        # does user want to fill with template ?
        template_name = None
        # show template chooser only if there are some templates
        if len(self.tpl_files) > 0:
            template_chooser = TemplateChooser(None, self.project_dir, self.tpl_files)

            if template_chooser.ShowModal() == wx.ID_CANCEL:
                return

            elif template_chooser.ShowModal() == wx.ID_OK:
                template_name = template_chooser.chosentemplate
                template_chooser.Destroy()


        if template_name == None:
            form = Form(None, self.fields_file, 'Fill in the values')            
        else:
            template_vals = yaml.load(open(template_name))
            form = Form(None, self.fields_file, 'Fill in the values', template_vals)

        if form.ShowModal() == wx.ID_OK:
            form.get_values()

            # Initialise lock as open
            form.vals['LOCK_STATUS'] = 'unlocked'
            self.records.insert_record(form.vals)

            # recreate index
            #self.register.index_summary = self.records.create_index()
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
            self.register.SetStatusText('No record selected', 0)
            return

        id = str(self.register.record_display.GetItemData(selected_record))

        record_vals = self.records.retrieve_record(id)

        if self.is_locked(selected_record):
            form = ReadOnlyForm(None, self.fields_file,
                        'Locked record. Cannot edit', record_vals)
            if form.ShowModal() == wx.ID_OK:
                form.Destroy
        else:
            form = Form(None, self.fields_file, 'Edit the values', record_vals)

            if form.ShowModal() == wx.ID_OK:
                form.get_values()
                # insert record with same id
                self.records.insert_record(form.vals, id)
                self.register.refresh_records()

            form.Destroy()
        

    def export_record(self, event):
        """Export the selected record into another project db.
        Matching fields are alone exported while others are ignored"""
        # get project to export to
        project_chooser = ProjectChooser(None, self.config)
        if project_chooser.ShowModal() == wx.ID_OK:
            chosen_project = project_chooser.default_project

        # cancel export otherwise
        else:
            return
         
        # Get the record vals
        selected_record = self.register.record_display.GetFirstSelected()
        if selected_record == -1:
            self.register.SetStatusText('No record selected', 0)
            return

        id = str(self.register.record_display.GetItemData(selected_record))
        record_vals = self.records.retrieve_record(id)
        record_vals['LOCK_STATUS'] = 'unlocked'

        # if same project is selected, clone it
        if chosen_project == self.config.options['default_project']:
            self.records.insert_record(record_vals)
            self.register.refresh_records()

        # if other project selected, open that db and enter compatible vals
        # get values for other project
        other_project_dir = self.config.options['projects'][chosen_project]
   
        # load paths for other project
        #self.fields_file = os.path.join(self.project_dir, 'fields.yaml')
        index_file = os.path.join(other_project_dir, 'index.yaml')
        db_file = os.path.join(other_project_dir, 'records.db')
        passfile = os.path.join(other_project_dir, 'pass.hsh')

        self.recipient_records = Records(db_file, index_file, passfile,
                                         self.config.options['num_backups'],
                                         self.config.options['backup_freq'])
        self.recipient_records.insert_record(record_vals)
        # TODO: close the loaded records
        
            
    def is_locked(self, record):
        """Is the record locked. record is index obained from the listctrl"""
        # last entry will always be lock status
        lock_status = self.register.record_display.GetItem(record,
                      len(self.records.index_fields)-1).GetText()

        if lock_status == 'locked':
            return True
        else:
            return False

        
    def toggle_lock(self):
        """Toggle the locked status of the selected record.
        Only priveleges user (admin) should be allowed to use this"""
        selected_record = self.register.record_display.GetFirstSelected()
        
        if selected_record == -1:
            self.register.SetStatusText('No record selected', 0)
            return

        id = str(self.register.record_display.GetItemData(selected_record))
        record_vals = self.records.retrieve_record(id)

        # if there is no lock_status, it is unlocked
        try:
            lock_status = record_vals['LOCK_STATUS']
        except KeyError:
            lock_status = 'unlocked'
        
        if lock_status == 'unlocked':
            record_vals['LOCK_STATUS'] = 'locked'
            self.register.SetStatusText('Locked selected record')
        else:
            record_vals['LOCK_STATUS'] = 'unlocked'
            self.register.SetStatusText('Unlocked selected record')

        self.records.insert_record(record_vals, id)
        self.register.index_summary = self.records.create_index()
        
        self.register.refresh_records()
            

    def flush_report(self, event):
        """Remove the stored raw report for the record if it exists"""
        selected_record = self.register.record_display.GetFirstSelected()

        if selected_record == -1:
            print 'No record selected'
            return

        id = str(self.register.record_display.GetItemData(selected_record))
        
        record_vals = self.records.retrieve_record(id)

        record_vals['raw_report'] = ''

        #self.records.delete_record(id)
        self.records.insert_record(record_vals, id)

        
    def show_n_edit_report(self, event):
        """Display the report for the selected record and allow edits"""
        selected_record = self.register.record_display.GetFirstSelected()

        if selected_record == -1:
            self.register.SetStatusText('No record selected', 0)
            return

        # convert to string coz unicode object does not work
        id = str(self.register.record_display.GetItemData(selected_record))
        
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
            rep = Report(template_file, record_vals, self.image_folder,
                         id, raw_report, local_stylefile)
        elif os.path.exists(global_stylefile):
            rep = Report(template_file, record_vals, self.image_folder,
                         id, raw_report, global_stylefile)
        else:
            rep = Report(template_file, record_vals, self.image_folder,
                         id, raw_report)

        raw_report =  rep.edit_report()
        
        record_vals['raw_report'] = raw_report
        self.records.insert_record(record_vals, id)

        
        
    def display_pdf(self, pdf_file):
        """Display the pdf using the native viewer"""
        if sys.platform.startswith('linux'):
            time.sleep(2)
            subprocess.Popen(['evince', pdf_file])

        elif sys.platform == 'win32':
            os.startfile(pdf_file)


    def summarize_numerical(self, fieldname, FILTER_SUMMARY):
        """Calculate summary for numerical data with
        field name (key) fieldname"""
        val_id_pairs = self.records.retrieve_column_with_id(fieldname)
        #col = self.records.retrieve_column(fieldname)
        # only restricted ids
        if FILTER_SUMMARY:
            vals = [val for (val, id) in val_id_pairs if id in self.register.restrict_ids]
        else:
            vals = [val for (val, id) in val_id_pairs]
        
        
        
        numerical_cols = [str2float(val) for val in vals if str2float(val) != '']

        # mean = numpy.mean(numerical_cols)
        # stdev = numpy.std(numerical_cols)
        mean, stdev = meanstdv(numerical_cols)
        minimum = min(numerical_cols)
        maximum = max(numerical_cols)
        total_vals = len(vals)
        missing_vals = total_vals - len(numerical_cols)
        
        return mean, stdev, minimum, maximum, total_vals, missing_vals


    def summarize_categorical(self, fieldname, FILTER_SUMMARY):
        """summarize categorical data"""
        val_id_pairs = self.records.retrieve_column_with_id(fieldname)
        uniq = {}

        # only restricted ids
        if FILTER_SUMMARY:
            vals = [val for (val, id) in val_id_pairs if id in self.register.restrict_ids]
        else:
            vals = [val for (val, id) in val_id_pairs]
        
        for val in vals:
            if val in uniq:
                uniq[val] += 1
            else:
                uniq[val] = 1

        result = []
        for key in uniq:
            result.append((key, str(uniq[key])))
              
        return result


    def cat_summary(self, event):
        #TODO: retrive fieldnames in init and dont keep repeating
        catsummary = CatSummary(self, self.get_fieldnames(self.fields_file))
        catsummary.Show()
    
    def num_summary(self, event):
        numsummary = NumSummary(self, self.get_fieldnames(self.fields_file))
        numsummary.Show()

    def get_fieldnames(self, fields_file):
        """retrieve the index names"""
        fieldnames = []
        fields_data = yaml.load_all(open(fields_file))

        for data in fields_data: #collection of dictionaries

            prefix = data.keys()[0]
            
            for i in range(len(data[prefix])):
                suffix = data[prefix][i][0]
                fieldnames.append(prefix + '_' + suffix)

        # for searching all
        fieldnames = ['Anywhere'] + fieldnames
        return fieldnames
                    
            

class WhatsNew(wx.Dialog):
    """
    Dialog announcing new features on new release
    """
    def __init__(self, parent, message):
        wx.Dialog.__init__(self, None, -1, "What is new?")

        # widgets
        panel = wx.Panel(self, -1)
        self.msgbox = wx.StaticText(panel, -1, label=message)
        self.ok_button = wx.Button(panel, -1, "OK")
        self.not_again_button = wx.Button(panel, -1, "Do not show again")

        # Bindings
        self.ok_button.Bind(wx.EVT_BUTTON, self.done)
        self.not_again_button.Bind(wx.EVT_BUTTON, self.not_again)

        # sizers
        panelsizer = wx.BoxSizer(wx.VERTICAL)
        buttonsizer = wx.BoxSizer(wx.HORIZONTAL)

        buttonsizer.Add(self.not_again_button, 0, wx.ALL, 10)
        buttonsizer.Add(self.ok_button, 0, wx.ALL, 10)
        panelsizer.Add(self.msgbox, 10, wx.ALL|wx.EXPAND, 2)
        panelsizer.Add(buttonsizer, 1, wx.ALL, 2)
        
        panel.SetSizer(panelsizer)

        mainsizer = wx.BoxSizer(wx.HORIZONTAL)
        mainsizer.Add(panel, 1, wx.EXPAND, 5)
        mainsizer.Fit(self)
        self.SetSize((400, 450))
        self.Layout()


    def done(self, event):
        self.EndModal(wx.ID_OK)
        self.Destroy()


    def not_again(self, event):
        """
        """
        # this should trigger removal of the message file
        self.EndModal(wx.ID_CANCEL)
        self.Destroy()


        
    
class TemplateChooser(wx.Dialog):
    """List the available templates and allow user to choose one"""
    def __init__(self, parent, project_dir, tpl_files):
        wx.Dialog.__init__(self, parent, -1, 'Choose template to use')

        self.project_dir = project_dir
        self.tpl_files = tpl_files
        self.templates = self.get_templates()

        # Default is empty
        self.chosentemplate = 'Empty'
        
        panel  = wx.Panel(self, -1)
        panelsizer = wx.BoxSizer(wx.VERTICAL)
        buttonsizer = wx.BoxSizer(wx.HORIZONTAL)

        self.choices = wx.RadioBox(panel, -1, "Choose template",
                                   choices=self.templates, style=wx.RA_VERTICAL)
        #self.cancel_button = wx.Button(panel, -1, 'Cancel')
        self.no_template_button = wx.Button(panel, -1, 'No template')
        self.use_template_button = wx.Button(panel, -1, 'Use template')

        #self.cancel_button.Bind(wx.EVT_BUTTON, self.cancel)
        self.no_template_button.Bind(wx.EVT_BUTTON, self.no_template)
        self.use_template_button.Bind(wx.EVT_BUTTON, self.use_template)

        buttonsizer.Add(self.no_template_button, 0, wx.ALL, 10)
        buttonsizer.Add(self.use_template_button, 0, wx.ALL, 10)

        panelsizer.Add(self.choices, 10, wx.ALL|wx.EXPAND, 2)
        panelsizer.Add(buttonsizer, 1, wx.ALL, 2)
        
        panel.SetSizer(panelsizer)

        mainsizer = wx.BoxSizer(wx.HORIZONTAL)
        mainsizer.Add(panel, 1, wx.EXPAND, 5)
        mainsizer.Fit(self)
        self.Layout()

        self.SetSize((300, 500))
        
    def _filename2templatename(self, name):
        """from filename, get the template name"""
        return os.path.basename(name)[:-4]

    
    def _templatename2filename(self, name):
        """from template name, get full filename"""
        return os.path.join(self.project_dir, name + '.tpl')
    
        
    def get_templates(self):
        """collect template names"""
        #tpl_files = glob.glob(os.path.join(project_dir, '*.tpl'))
        return [self._filename2templatename(filename) for filename in self.tpl_files]


    def cancel(self, event):
        """Cancel and discard edits"""
        self.EndModal(wx.ID_CANCEL)


    def no_template(self, event):
        self.chosentemplate = None
        self.EndModal(wx.ID_OK)
        
    def use_template(self, event):
        """returns the filename to the template file"""
        self.chosentemplate = self._templatename2filename(
                              self.choices.GetStringSelection())
        self.EndModal(wx.ID_OK)

        
# TODO: integrate this with template chooser
class ProjectChooser(wx.Dialog):
    """List the registered projects, show the default project
    and allow user to choose a new one"""
    def __init__(self, parent, config_dict):
        # config is dict of options loaded by the project manager
        wx.Dialog.__init__(self, parent, -1, 'Choose project to load')

        self.config_dict = config_dict
        (self.project_names, self.project_paths,
         self.default_project) = self.get_projects()

        panel  = wx.Panel(self, -1)
        panelsizer = wx.BoxSizer(wx.VERTICAL)
        buttonsizer = wx.BoxSizer(wx.HORIZONTAL)

        self.choices = wx.RadioBox(panel, -1, "Choose project",
                                   choices=self.project_names, style=wx.RA_VERTICAL)
        # set default project
        self.choices.SetSelection(self.default_project)
        self.cancel_button = wx.Button(panel, -1, 'Cancel')
        self.done_button = wx.Button(panel, -1, 'Done')

        self.cancel_button.Bind(wx.EVT_BUTTON, self.cancel)
        self.done_button.Bind(wx.EVT_BUTTON, self.ondone)

        buttonsizer.Add(self.cancel_button, 0, wx.ALL, 10)
        buttonsizer.Add(self.done_button, 0, wx.ALL, 10)

        panelsizer.Add(self.choices, 10, wx.ALL|wx.EXPAND, 2)
        panelsizer.Add(buttonsizer, 1, wx.ALL, 2)
        
        panel.SetSizer(panelsizer)

        mainsizer = wx.BoxSizer(wx.HORIZONTAL)
        mainsizer.Add(panel, 1, wx.EXPAND, 5)
        mainsizer.Fit(self)
        self.Layout()

        
    def get_projects(self):
        """collect projects details"""
        project_names = [os.path.basename(pth)
                         for pth in self.config_dict.options['projects']]
        return (project_names, self.config_dict.options['projects'],
                self.config_dict.options['default_project'])
    

    def cancel(self, event):
        """Cancel and discard edits"""
        self.EndModal(wx.ID_CANCEL)
        

    def ondone(self, event):
        """returns the filename to the template file"""
        self.default_project = self.choices.GetSelection()
        self.EndModal(wx.ID_OK)
        

    
class Register(wx.Frame):
    """Display the index and allow selection and operation on records"""

    def __init__(self, parent, records, project_name):
        """records is a Records instance - provides the db functions"""
        wx.Frame.__init__(self, None, -1, project_name, size=(720, 900))

        self.parent = parent
        self.records = records

        # no filter
        #self.restrict_ids = records.db.keys()
        self.FILTER = False  # flag if filter is applied
                
        self.hbox1 = wx.BoxSizer(wx.HORIZONTAL) # for the listctrl
        self.hbox2 = wx.BoxSizer(wx.HORIZONTAL) # for the buttons
        self.vbox = wx.BoxSizer(wx.VERTICAL) # for the panel
        self.hbox3 = wx.BoxSizer(wx.HORIZONTAL) # for the filter controls

        panel = wx.Panel(self, -1)

        # filter for records
        self.fieldnames = parent.get_fieldnames(parent.fields_file)
        self.filter_label = wx.ComboBox(panel, -1, choices=self.fieldnames)
        self.filter_operator = wx.ComboBox(panel, -1,
                               choices=['==', '<' ,'>', 'contains', 'starts with'])
        self.filter_value = wx.TextCtrl(panel, -1, style=wx.TE_PROCESS_ENTER)
        
        # load the records and create index
        self.index_summary = self.records.create_index()
        # listcontrol - number of cols to sort, add 1 for locking
        self.record_display = AutoWidthListCtrl(panel, len(self.records.index_fields))

        # buttons
        self.edit_button = wx.Button(panel, -1,  'View / Edit Record')
        self.new_button = wx.Button(panel, -1, 'New Record')
        self.remove_button = wx.Button(panel, -1, 'Remove Record')
        
        self.hbox1.Add(self.record_display, 1, wx.ALL|wx.EXPAND, 10)
        self.hbox2.Add(self.new_button, 1, wx.ALL, 5) 
        self.hbox2.Add(self.edit_button, 1, wx.ALL, 5)
        self.hbox2.Add(self.remove_button, 1, wx.ALL, 5)
        self.hbox3.Add(self.filter_label, 1, wx.ALL, 5)
        self.hbox3.Add(self.filter_operator, 1, wx.ALL, 5)
        self.hbox3.Add(self.filter_value, 1, wx.ALL, 5)

        self.vbox.Add(self.hbox3, 1, wx.ALL|wx.EXPAND, 10)
        self.vbox.Add(self.hbox1, 6, wx.EXPAND, 10)
        self.vbox.Add(self.hbox2, 1, wx.ALL|wx.EXPAND, 10)

        self._build_menubar()
        self._set_bindings()

        panel.SetSizer(self.vbox)

        mainsizer = wx.BoxSizer(wx.HORIZONTAL)
        mainsizer.Add(panel, 1, wx.EXPAND, 5)
        mainsizer.Fit(self)
        self.Layout()
        # self.SetSizer(mainsizer)
        self.SetSize((640, 720))
        
        self.CreateStatusBar(2)
        
        #self.Layout()
        self.Centre()
        self.Show(True)
        self.load_records()


    def _build_menubar(self):
        """Build the menu bar"""
        self.MenuBar = wx.MenuBar()

        file_menu = wx.Menu()
        #file_menu.Append(ID_NEW, "&New Record","Create a new record")
        #file_menu.Append(ID_EDIT, "&Edit Record", "Edit an existing record")
        file_menu.Append(ID_PROJ, "&Change Project", "Load a new project")
        #file_menu.Append(ID_LOCK, "&Toggle Lock", "Toggle locking of record")
        #file_menu.Append(ID_REMOVE, "&Remove Record", "Remove existing record")
        file_menu.Append(ID_FLUSH, "&Flush report", "Remove stored report")
        file_menu.Append(ID_EXPORT, "&Export", "Export records as csv")
        file_menu.Append(ID_QUIT, "&Quit","Quit the program")
   
        edit_menu = wx.Menu()
        edit_menu.Append(ID_PREF, "Preferences", "Edit preferences")
        edit_menu.Append(ID_PASS, "Change Password", "Change Admin Password")

        record_menu = wx.Menu()
        record_menu.Append(ID_NEW, "&New Record", "Create a new record")
        record_menu.Append(ID_EDIT, "&Edit Record", "Edit existing record")
        record_menu.Append(ID_LOCK, "&Toggle Lock\tCtrl-T", "Toggle locking of record")
        record_menu.Append(ID_RECEXPORT, "&Export Record", "Export to another project")        
        record_menu.Append(ID_REMOVE, "Remove Record", "Remove existing record")
        
        
        report_gen_menu = wx.Menu()
        for i in range(len(self.parent.report_files)):
            report_name = os.path.basename(self.parent.report_files[i]).rstrip('.rst')
            report_gen_menu.Append(2*i, report_name)


        template_menu = wx.Menu()
        template_menu.Append(ID_NEWTEMPLATE, "&New Template", "Create a new template")
        template_menu.Append(ID_DELTEMPLATE, "&Delete Template", "Delete a template")

        info_menu = wx.Menu()
        info_menu.Append(ID_NUM_SUMMARY, "&Numerical Summary", "Provide summary for numerical data")
        info_menu.Append(ID_CAT_SUMMARY, "&Categorical Summary", "Provide summary for categorical data")
        
        self.MenuBar.Append(file_menu, "&File")
        self.MenuBar.Append(record_menu, "&Record")
        self.MenuBar.Append(edit_menu, "&Edit")
        self.MenuBar.Append(report_gen_menu, "&Generate Report")
        self.MenuBar.Append(template_menu, "&Template")
        self.MenuBar.Append(info_menu, "&Info")
        
        self.SetMenuBar(self.MenuBar)

        
    def _set_bindings(self):
        """All the bindings"""
        self.Bind(wx.EVT_CLOSE, self.on_quit)
        self.new_button.Bind(wx.EVT_BUTTON, self.parent.new_record)
        self.edit_button.Bind(wx.EVT_BUTTON, self.parent.edit_record)
        self.remove_button.Bind(wx.EVT_BUTTON, self.remove_record)
        
        self.Bind(wx.EVT_MENU, self.parent.new_record, id=ID_NEW)
        self.Bind(wx.EVT_MENU, self.parent.change_project, id=ID_PROJ)
        self.Bind(wx.EVT_MENU, self.parent.edit_record, id=ID_EDIT)
        self.Bind(wx.EVT_MENU, self.parent.export_record, id=ID_RECEXPORT)        
        self.Bind(wx.EVT_MENU, self.toggle_lock, id=ID_LOCK)
        self.Bind(wx.EVT_MENU, self.change_pass, id=ID_PASS)
        self.Bind(wx.EVT_MENU, self.export_records, id=ID_EXPORT)
        self.Bind(wx.EVT_MENU, self.parent.flush_report, id=ID_FLUSH)
        self.Bind(wx.EVT_MENU, self.parent.new_template, id=ID_NEWTEMPLATE)
        self.Bind(wx.EVT_MENU, self.parent.del_template, id=ID_DELTEMPLATE)
        self.Bind(wx.EVT_MENU, self.parent.num_summary, id=ID_NUM_SUMMARY)
        self.Bind(wx.EVT_MENU, self.parent.cat_summary, id=ID_CAT_SUMMARY)
        self.Bind(wx.EVT_MENU, self.on_quit, id=ID_QUIT)

        # double click on record opens it for edit / read
        self.record_display.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.parent.edit_record)
        self.record_display.Bind(wx.EVT_LIST_COL_CLICK, self.refresh_row_colors)
        
        self.filter_value.Bind(wx.EVT_TEXT_ENTER, self.apply_filter)
        #self.filter_operator.Bind(wx.EVT_TEXT_ENTER, self.apply_filter)
        
        # all generate report events are bound to one function
        for i in range(len(self.parent.report_files)):
            self.Bind(wx.EVT_MENU, self.parent.show_n_edit_report, id=2*i)


    def export_records(self, event):
        """
        Export selected fields from selected records 
        """
        export_dlg = ExportDlg(self, self.records.db)
        if export_dlg.ShowModal() == wx.ID_OK:
            pass

        #print export_options
            
            
    def load_records(self):
        """Load the index and display"""
        # for sorting we use the full db
        # itemdatamap must be a dict
        self.record_display.itemDataMap = self.index_summary

        index_keys = self.records.index_fields

        # create the columns
        for i, val in enumerate(index_keys):
            keyname = val.split('_')[1]
            self.record_display.InsertColumn(i, keyname)

        for key in self.index_summary:
            self.record_display_append(self.index_summary[key], key)

        # display total records in status
        self.SetStatusText('%s records'  %(len(self.index_summary)))


    def toggle_lock(self, event):
        """If user has admin priveleges, allow him
        to toggle lock status of selected record"""
        #TODO: check if record is selected before asking password
        if self.user_has_key():
            self.parent.toggle_lock()

        else:
            self.SetStatusText('Authentication failed')
            

    def user_has_key(self):
        """Check if user knows password"""
        passdlg = wx.PasswordEntryDialog(self, 'Enter password')
        if passdlg.ShowModal() == wx.ID_OK:
            entry = passdlg.GetValue()
            passdlg.Destroy()
            if hashlib.md5(entry).hexdigest() == self.records.passhash:
                return True
        else:
            return False


    def change_pass(self, event):
        """User wants to change password"""
        if self.user_has_key():
            newpassdlg = wx.PasswordEntryDialog(self, 'Enter new password')
            if newpassdlg.ShowModal() == wx.ID_OK:
                newentry = newpassdlg.GetValue()
                newpasshash = hashlib.md5(newentry).hexdigest()
                with open(self.parent.passfile, 'w') as f:
                    f.write(newpasshash)
                self.SetStatusText('Password changed successfully')
            else:
                self.SetStatusText('Password not changed')

        else:
            self.SetStatusText('Incorrect password')
                
        
        
    def refresh_records(self):
        """Completely refresh the summary being shown"""
        # store currently sorted column and sort direction
        col, direction = self.record_display.GetSortState()
        self.record_display.ClearAll()
        
        if self.FILTER:
            self.index_summary = self.records.create_index(self.restrict_ids)
        else:
            self.index_summary = self.records.create_index()
            
        self.load_records()
        self.record_display.SortListItems(col, direction)
        # refresh the row hightlighting
        self.record_display.RefreshRows()

    def refresh_row_colors(self, event):
        """When column header is clicked, sort the col
        and then refresh row colouring"""
        col_clicked = event.Column
        last_column, ascending = self.record_display.GetSortState()

        direction = 1
        if last_column == col_clicked:
            direction = not ascending # toggle between 0 and 1
            
        self.record_display.SortListItems(event.Column, direction)
        self.record_display.RefreshRows()         


    def apply_filter(self, event):
        """Restrict the record display according to the applied filter"""
        # Read the filter parameters
        filter_label = self.filter_label.GetValue()
        filter_label = self.without_parentheses(filter_label)
        filter_operator = self.filter_operator.GetValue()
        filter_value = self.filter_value.GetValue()

        # vlaidate the filter
        NUM = filter_operator in ['<', '>']

        val_id_pairs = self.records.retrieve_column_with_id(filter_label)
        
        # numerical
        # separate into vals coaxable into numbers and those no
        if NUM:
            nums = [(str2float(val), id) for (val, id) in val_id_pairs if str2float(val) != '']
            #innums = [(val, id) for (val, id) in val_id_pairs if str2float(val) == '']
            
            if len(nums) == 0:
                self.SetStatusText('No numerical values in ', filter_label)
                return

            # TODO: make this secure
            filt_vals = [(val, id) for (val, id) in nums
                         if eval(''.join([str(val), filter_operator, filter_value]))]

            
        # strings
        else:
            if filter_operator == 'contains':
                filt_vals = [(val, id) for (val, id) in val_id_pairs
                             if filter_value.lower() in val.lower()]
            elif filter_operator == 'starts with':
                filt_vals = [(val, id) for (val, id) in val_id_pairs
                             if val.lower().startswith(filter_value.lower())]

        # create list of ids to restrict to
        self.restrict_ids = [id for (val, id) in filt_vals]

        self.FILTER = True
        # TODO: Need a clear filter to remove this
                
        # refresh register display
        self.index_summary = self.records.create_index(self.restrict_ids)
        self.refresh_records()



    def without_parentheses(self, label_str):
        """Remove terminal text within parentheses
        >>> without_parentheses(self, "test(within)")
            "test"
        """
        # TODO: refactor to avoid repetitions of this function
        opening_brace_pos = label_str.find('(')

        if opening_brace_pos == -1:
            return label_str
        
        return label_str[:opening_brace_pos].strip()

        
        
    def record_display_append(self, rec, key):
        """add the rec to display"""
        # convert everything to a string
        rec = [str(x) for x in rec]

        id = self.record_display.InsertStringItem(sys.maxint, rec[0])

        for col in range(1, len(rec)):
            self.record_display.SetStringItem(id, col, rec[col])

        # alternate row colours
        # if id % 2:
        #     self.record_display.SetItemBackgroundColour(id, "white")
        # else:
        #     self.record_display.SetItemBackgroundColour(id, GREY)
            
        self.record_display.SetItemData(id, key)
            
        
    def on_quit(self, event):
        """Things to do on exiting"""
        self.records.db.close()
        sys.exit()

        
    def remove_record(self, event):
        """delete the selected record"""
        selected_record = self.record_display.GetFirstSelected()

        if selected_record == -1:
            self.SetStatusText('No record selected', 0)
            return
        
        id = str(self.record_display.GetItemData(selected_record))

        # id = str(''.join([self.record_display.GetItem(
        #                 selected_record, x).GetText()
        #                 for x in range(len(self.records.index_keys))]))

        if self.parent.is_locked(selected_record):
            self.SetStatusText('Cannot delete locked record')
            return
        
        self.records.delete_record(id)
        
        self.index_summary = self.records.create_index()
        self.refresh_records()

        

class AutoWidthListCtrl(wx.ListCtrl, ListCtrlAutoWidthMixin, ColumnSorterMixin, ListRowHighlighter):
    def __init__(self, parent, columns_to_sort):
        # columns_to_sort is number of columns
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT)
        ListCtrlAutoWidthMixin.__init__(self)
        ColumnSorterMixin.__init__(self, columns_to_sort)
        ListRowHighlighter.__init__(self)
        
    def GetListCtrl(self):
        return self


class ExportDlg(wx.Dialog):
    """Collect options for export"""
    def __init__(self, parent, record_db):
        wx.Dialog.__init__(self, parent, -1, "Export as csv")
        self.parent = parent
        fieldnames = [self.without_parentheses(f) for f in parent.fieldnames]
        
        panel = wx.Panel(self, -1)
        self.clbox = wx.CheckListBox(panel, -1, choices = fieldnames)
        self.cancel_button = wx.Button(panel, -1, 'Cancel')
        self.export_button = wx.Button(panel, -1, 'Export')

        self.cancel_button.Bind(wx.EVT_BUTTON, self.cancel)
        self.export_button.Bind(wx.EVT_BUTTON, self.export)

        panelsizer = wx.BoxSizer(wx.VERTICAL)
        buttonsizer = wx.BoxSizer(wx.HORIZONTAL)
        
        buttonsizer.Add(self.cancel_button, 0, wx.ALL, 10)
        buttonsizer.Add(self.export_button, 0, wx.ALL, 10)
        panelsizer.Add(self.clbox, 8, wx.ALL|wx.EXPAND, 2)
        panelsizer.Add(buttonsizer, 2, wx.ALL, 2)

        panel.SetSizer(panelsizer)
        mainsizer = wx.BoxSizer(wx.HORIZONTAL)
        mainsizer.Add(panel, 1, wx.EXPAND, 5)
        mainsizer.Fit(self)
        self.Layout()
        
        self.record_db = record_db
        #self.export()

        #self.fieldnames = self.parent.

    def cancel(self, event):
        """
        """
        self.EndModal(wx.ID_CANCEL)
    
        
    def export(self, event):
        """
        """
        fields = self.clbox.GetCheckedStrings()
        savedlg = wx.FileDialog(self, "Choose file to save...", 
                    style=wx.SAVE | wx.OVERWRITE_PROMPT)

        if savedlg.ShowModal() == wx.ID_OK:
            savefilename = savedlg.GetPath()
            #savedlg.Destroy()
        else:
            return

        writer = csv.writer(open(savefilename, 'wb'))
        #TODO: filters for the records
        for rec in self.record_db:
            if rec in self.parent.restrict_ids:
                row = [self.record_db[rec][field] for field in fields]
                writer.writerow(row)
        self.EndModal(wx.ID_OK)
            

    # reusing function from pane class
    def without_parentheses(self, label_str):
            """Remove terminal text within parentheses
            >>> without_parentheses(self, "test(within)")
                "test"
            """
            opening_brace_pos = label_str.find('(')

            if opening_brace_pos == -1:
                return label_str

            return label_str[:opening_brace_pos].strip()


def test():
    app= wx.App()
    rm = ReportManager()
    #rm.Show(True)
    app.MainLoop()

if __name__ == '__main__':
    test()    
