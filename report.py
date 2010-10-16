#!/usr/bin/env python

"""Use supplied dictionary of values and a template to fill in the template
with mako and render the report to a pdf with rst2pdf"""

import wx
import subprocess
import tempfile
from mako.template import Template
from rst2pdf.createpdf import RstToPdf

class Report():
    """
    """
    def __init__(self, template_file, vals, raw_report='', stylefile=None):
        """template_file is full path to a .rst file that is the template.
        vals is a dictionary containing the variable value.
        raw_report is previously generated filled template if stored.
        stylefile is a .sty file for rst2pdf
	"""
        #self.template_file = template_file
        self.vals = vals
        self.raw_report = raw_report
        self.stylefile = stylefile

        self.template = Template(filename=template_file)

        # create a new report only if there isnt one stored
        if self.raw_report == '':
            self.generate_raw()


    def generate_raw(self, event=None):
        """fill the template to create a raw_report"""
        self.raw_report = self.template.render(vals=self.vals)
        

    def generate_pdf(self):
        """Creat pdf and return path to pdf file"""
        # get the temp names
        tmp_rstfilename = tempfile.mkstemp(suffix='.rst')[1]
        tmp_pdffilename = tempfile.mkstemp(suffix='.pdf')[1]

        print tmp_rstfilename
        
        # write the raw_report as a file
        with open(tmp_rstfilename,'w') as fi:
            fi.write(self.raw_report)

        # invoke rst2pdf
        if self.stylefile:
            cmd = ['rst2pdf', '-s', self.stylefile, '-o', tmp_pdffilename, tmp_rstfilename]
        else:
            cmd = ['rst2pdf', '-o', tmp_pdffilename, tmp_rstfilename]

        subprocess.Popen(cmd)
        return tmp_pdffilename


    def edit_report(self):
        """Present a simple editor to edit the raw_report"""
        #app = wx.App()
        ed = Editor(None, self.raw_report)
        if ed.ShowModal() == wx.ID_OK:
            self.raw_report = ed.text
        ed.Destroy()
        #app.MainLoop()
        return self.raw_report
    
class Editor(wx.Dialog):
    """A simple text editor"""
    def __init__(self, parent, text):
        wx.Dialog.__init__(self, parent, -1, 'Edit Report')

        self.text = text
        
        panel = wx.Panel(self, -1)
        panelsizer = wx.BoxSizer(wx.VERTICAL)
        buttonsizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.textcontrol = wx.TextCtrl(panel, -1, style=wx.TE_MULTILINE|wx.TE_RICH)
        self.cancel_button = wx.Button(panel, -1, 'Cancel')
        self.done_button = wx.Button(panel, -1, 'Done')

        self.cancel_button.Bind(wx.EVT_BUTTON, self.cancel)
        self.done_button.Bind(wx.EVT_BUTTON, self.ondone)
        
        buttonsizer.Add(self.cancel_button, 0, wx.ALL, 10)
        buttonsizer.Add(self.done_button, 0, wx.ALL, 10)
        
        panelsizer.Add(self.textcontrol, 10, wx.ALL|wx.EXPAND, 2)
        panelsizer.Add(buttonsizer, 1, wx.ALL, 2)

        panel.SetSizer(panelsizer)
        self.Layout()

        self.textcontrol.write(text)

       # self.ShowModal()

        
    def cancel(self, event):
        """Cancel and discard edits"""
        self.EndModal(wx.ID_CANCEL)

    def ondone(self, event):
        """return the modified text"""
        self.text = self.textcontrol.GetValue()
        self.EndModal(wx.ID_OK)
        

def editor_test():
    """Testing the editor"""
    app = wx.App()
    ed = Editor(None, 'This is a test')
    if ed.ShowModal() == wx.ID_OK:
        print ed.text
    ed.Destroy()
    
    app.MainLoop()
        

def test():
    """Test the report module and demonstrate use"""
    #def __init__(self, template_file, vals, raw_report='', stylefile=None):
    template_file = 'test/template.rst'
    vals = {'Demographics_Name':'Raja',
            'Demographics_Age':36,
            'Demographics_Sex':'Male',
            'Clinical_Presentation':'Asymptomatic',
            'Clinical_Drugs':'Aspirin 75 mg PO OD',
            'Clinical_ECG':'Normal Sinus Rhythm'}

    print 'creating new report with a template and values'
    rep = Report(template_file, vals)
    rep.generate_raw()
    print rep.raw_report

    rep.edit_report()
    #print "path to pdf file"
    #pdf =  rep.generate_pdf()
    #print pdf


if __name__ == '__main__':
    #editor_test()
    test()
