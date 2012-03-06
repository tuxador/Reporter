#!/usr/bin/env python

"""
Framework for creating reports using a template and user input.

Template is a mako template with variables.
A separate file lists the variables and the wx control
required to get user input (see input_fields.yaml)

The input fields file is loaded using yaml. Based on this,
the controls are created and presented to the user. Once the user
has entered the values, mako is used to render the template and create
an rst document. This is converted to pdf using rst2pdf"""


##
# Author: Raja Selvaraj <rajajs@gmail.com>
# License: GPL
##

import wx
import yaml
import wx.lib.scrolledpanel as scrolled

from datectrl import DateCtrl



class ReadOnlyForm(wx.Dialog):
    def __init__(self, parent, fields_file, project_name='', input_vals=None):
        """fields_file is the file to use to construct fields
        input_vals is a dict with the initial values.
        project_name is a string that is the name of the whole project"""
        # modification of the Form class
        wx.Dialog.__init__(self, parent, -1, size=(600, 700))

        self.panel = FormPanel(self, fields_file, project_name)

        self.parent = parent
        self.input_vals = input_vals
        self.project_name = project_name
        self.vals = {} # init the dict

        #self.reset_button = wx.Button(self.panel, label = 'Reset form')
        #self.cancel_button = wx.Button(self.panel, id=wx.ID_CANCEL, label="Cancel")
        self.done_button = wx.Button(self.panel, id=wx.ID_OK, label= 'Done')

        #self.cancel_button.Bind(wx.EVT_BUTTON, self.cancel)
        #self.reset_button.Bind(wx.EVT_BUTTON, self.reset)
        self.done_button.Bind(wx.EVT_BUTTON, self.done)

        self.panel._layout()
        self.panel.panes[0].Collapse(False)

        mainsizer = wx.BoxSizer(wx.HORIZONTAL)
        mainsizer.Add(self.panel, 1, wx.EXPAND, 5)
        mainsizer.Fit(self)
        self.Layout()
        self.SetSize((600, 600))


        self.Show(True)

        if input_vals != None:
            self.set_values(input_vals)  # set the input values
            self.init_values = input_vals
        else:
            #self.get_values()
            #self.init_values = self.vals.copy()
            pass
        

    def set_values(self, vals):
        """Fill in the form according to the dict vals"""
        for label, control in zip(self.panel.labels, self.panel.controls):
            # TODO: change font
            try:
                control.SetLabel(vals[label])
            except TypeError: # coerce int to string if reqd
                control.SetLabel(str(vals[label]))
            except KeyError:
                pass


    def cancel(self, event):
        """Return without making any changes"""
        #self.vals = self.init_values  # negate any changes
        self.EndModal(wx.ID_CANCEL)
            
    def reset(self, event):
        """Reset to original stage"""
        self.set_values(self.init_values)

    def done(self, event):
        self.EndModal(wx.ID_OK)


class FormPanel(scrolled.ScrolledPanel):
    """A Frame  with several collapsible sections that contain
    parts of the form"""
    def __init__(self, parent, fields_file, title):
        scrolled.ScrolledPanel.__init__(self,parent, -1)

        ## contents of the panel
         # title at top
         # button at bottom
         # collpasible panes in between
        self.title = wx.StaticText(self, label=title)
        self.title.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.parent = parent
        
        # Panes will be constructed from yaml file
        self.panes = []
        self.construct_panes(fields_file)
        #self.make_pane_content(self.cp1.GetPane())
        
        #self._layout()
        self.SetAutoLayout(1)
        self.SetupScrolling()
        #self.Show(True)
        
    def _layout(self):
        """Layout the controls using sizers"""
        sizer = wx.BoxSizer(wx.VERTICAL)
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        sizer.Add(self.title, 0, wx.ALL, 25)

        for cp in self.panes:
            sizer.Add(cp, 0, wx.RIGHT|wx.LEFT|wx.EXPAND, 25)

        #button_sizer.Add(self.parent.reset_button, 0, wx.ALL, 25)
        #button_sizer.Add(self.parent.cancel_button, 0, wx.ALL, 25)
        button_sizer.Add(self.parent.done_button, 0, wx.ALL, 25)
        
        sizer.Add(button_sizer, 0 ,wx.ALL)
        self.SetSizer(sizer)

    def construct_panes(self, fields_file):
       """Read the fields file and use the data to construct the
       collapsible panes"""
       fields_data = yaml.load_all(open(fields_file))
       # Maintain master list of all labels and controls
       self.labels = []
       self.controls = []
       
       for pane_data in fields_data:
           self.panes.append(Pane(self, pane_data))
           self.labels += self.panes[-1].labels
           self.controls += self.panes[-1].controls
           
       self.Layout()

    def on_pane_changed(self, event):
        """When a pane uncollapses, make sure other panes are collapsed"""
        active_pane = event.EventObject
        if not event.GetCollapsed():
            for pane in self.panes:
                pane.Collapse(pane != active_pane)

        # set focus on first control in the active pane #TODO: causes segmentation fault
        #active_pane.controls[0].SetFocus()
        
                

class Pane(wx.CollapsiblePane):
    """Individual collapsible pane which can construct the controls,
    build the pane and read the values out"""
    def __init__(self, parent, pane_data):
        """pane_data is the data defining the controls in the form of
        a dictionary read from the yaml file"""
        self.panel = parent
        
        self.name = pane_data.keys()[0]
        self.pane_data = pane_data[self.name]

        wx.CollapsiblePane.__init__(self, parent, label=self.name,
                                    style=wx.CP_DEFAULT_STYLE|wx.CP_NO_TLW_RESIZE)
        widget_list =  self.make_content()

        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.on_collapse_state_changed)

        #widget_list = []
        self.make_layout(widget_list)

        
    def on_collapse_state_changed(self, event):
        self.panel.on_pane_changed(event)
        self.panel.Layout()


    def without_parentheses(self, label_str):
        """Remove terminal text within parentheses
        >>> without_parentheses(self, "test(within)")
            "test"
        """
        opening_brace_pos = label_str.find('(')

        if opening_brace_pos == -1:
            return label_str
        
        return label_str[:opening_brace_pos].strip()

    
    def make_content(self):
       """Put in the contents of the given pane based on the data.
       Data is a dict with index as keys and a list describing the
       widget as the value. See form_fields.yaml for examples.

       Pane content that is constructed are a widgetlist to go into the
       sizer, list of labels and list of controls"""
       self.labels = []
       self.control_labels = []
       self.controls = []
       self.pane = self.GetPane()
       
       # Use indices for looping as dict does not preserve order
       for i in range(len(self.pane_data)):
           control_data = self.pane_data[i]
           label = control_data[0]
           #control_type = control_data[1]

           # keep a list of labels
           self.labels.append(self.name + '_' +
                              self.without_parentheses(label))

           # statictext label
           self.control_labels.append(wx.StaticText(self.pane, -1, label,
                                            style=wx.ALIGN_CENTER_VERTICAL))
           BOLDFONT = wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.BOLD)
           self.control_labels[-1].SetFont(BOLDFONT)
           
           #
           self.controls.append(wx.StaticText(self.pane, -1))

       # make widget list - keep as loop so any additional steps can be added
       widget_list = []
       for l, c in zip(self.control_labels, self.controls):
           widget_list.append(l)
           widget_list.append((c, 1, wx.EXPAND))

       return widget_list

    
    def make_layout(self, widget_list):
        """Put in the contents of the pane"""
        fsizer = wx.FlexGridSizer(cols=2, hgap=5, vgap=5)
        fsizer.AddGrowableCol(1)
        fsizer.AddMany(widget_list)

        # border
        border = wx.BoxSizer(wx.HORIZONTAL)
        border.Add(fsizer, 1, wx.EXPAND|wx.ALL, 10)
        
        self.pane.SetSizer(border)


    def get_values(self):
        """Read all the values"""
        vals = {}
        for label, control in zip(self.labels, self.controls):
            vals[label] = control.GetValue()
        return vals




def test():
    """Test all modules in this script. Also serves as demo"""
    import pprint
    app = wx.App()

    print 'simple form'
    f = Form(None, 'test/fields.yaml')
    if f.ShowModal() == wx.ID_OK:
        f.get_values()
        pprint.pprint(f.vals)
    f.Destroy()

    print 'form with vaues'
    f = Form(None, 'test/fields.yaml', 'Featured', {'Demographics_Name':'Raja',
                                   'Clinical_Presentation':'Asymptomatic'})

    if f.ShowModal() == wx.ID_OK:
        f.get_values()
        pprint.pprint(f.vals)
    f.Destroy()
    
    
    app.MainLoop()
        
if __name__ == '__main__':
    test()
    # app = wx.App()
    # f = Form(None, 'report_docs/form_fields.yaml')
    # app.MainLoop()
