#!/usr/bin/env python

"""Use supplied dictionary of values and a template to fill in the template
with mako and render the report to a pdf with rst2pdf"""

import wx
import subprocess
import wx.lib.wxcairo as wxcairo
import poppler
import time

import tempfile
from mako.template import Template
#from rst2pdf.createpdf import RstToPdf

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

        print cmd
        subprocess.Popen(cmd)
        return tmp_pdffilename


    def edit_report(self):
        """Present a simple editor to edit the raw_report"""
        #app = wx.App()
        reped = ReportEditor(None, self, self.raw_report)
        if reped.ShowModal() == wx.ID_OK:
            self.raw_report = reped.raweditor.GetValue()
        reped.Destroy()
        #app.MainLoop()
        return self.raw_report
    
class Editor(wx.Dialog):
    """A simple text editor"""
    def __init__(self, parent, text):
        wx.Dialog.__init__(self, parent, -1, 'Edit Report',
                           style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)

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
        

class ReportEditor(wx.Dialog):
    def __init__(self, parent, report, raw_text):
        # begin wxGlade: Frame.__init__
        #wx.Frame.__init__(self, *args, **kwds)
        self.raw_text = raw_text
        self.report = report
        wx.Dialog.__init__(self, parent, -1, 'Edit Report',
                           style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)

        self.mainpanel = wx.Panel(self, -1)

        self.splitter = wx.SplitterWindow(self.mainpanel, -1, style=wx.SP_3D|wx.SP_BORDER)
        #self.splitter.SetMinimumPanesize(20)
        self.editorpanel = wx.Panel(self.splitter, -1)
        self.pdfpanel = wx.Panel(self.splitter, -1)
        self.splitter.SetMinimumPaneSize(20)

        self.buttonpanel = wx.Panel(self.pdfpanel, -1)
        self.buttonpanel2 = wx.Panel(self.editorpanel, -1)

        self.pdfviewer = PDFWindow(self.pdfpanel)
        self.raweditor = wx.TextCtrl(self.editorpanel, -1, "text editor",
                                     style=wx.TE_MULTILINE)

        self.prev_button = wx.Button(self.buttonpanel, -1, "Prev Page")
        self.next_button = wx.Button(self.buttonpanel, -1, "Next Page")
        self.refresh_button = wx.Button(self.buttonpanel, -1, "Refresh")
        
        self.revertbutton = wx.Button(self.buttonpanel2, -1, "Revert")
        self.donebutton = wx.Button(self.buttonpanel2, wx.ID_OK, "Done")

        self.__set_properties()
        self.__do_layout()

        self._set_bindings()
        self._init_values()
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: Frame.__set_properties
        self.SetTitle("Report Editor")

    def _set_bindings(self):
        """Bindings"""
        self.Bind(wx.EVT_BUTTON, self.prev_page, self.prev_button)
        self.Bind(wx.EVT_BUTTON, self.ondone, self.donebutton)

# end wxGlade
    def _init_values(self):
        """Initialise values in texteditor and pdf viewer"""
        pdf_file = self.report.generate_pdf()
        time.sleep(2)
        
        self.raweditor.write(self.raw_text)
        self.pdfviewer.LoadDocument(pdf_file)
        
        

    def __do_layout(self):
        # begin wxGlade: Frame.__do_layout
        rootsizer = wx.BoxSizer(wx.VERTICAL)
        mainsizer = wx.BoxSizer(wx.VERTICAL)
        editorpanel_sizer = wx.BoxSizer(wx.VERTICAL)
        buttonpanel2_sizer = wx.BoxSizer(wx.HORIZONTAL)
        pdfpanel_sizer = wx.BoxSizer(wx.VERTICAL)
        buttonpanel_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.splitter.SplitHorizontally(self.pdfpanel, self.editorpanel)
        #self.splitter.SetMinimumPaneSize(20)
        #self.splitter.SetSashPosition(100)        
        mainsizer.Add(self.splitter, 1, wx.EXPAND, 0)

        buttonpanel_sizer.Add(self.prev_button, 0, wx.ALL, 10)
        buttonpanel_sizer.Add(self.next_button, 0, wx.ALL, 10)
        buttonpanel_sizer.Add(self.refresh_button, 0, wx.ALL, 10)
        self.buttonpanel.SetSizer(buttonpanel_sizer)

        pdfpanel_sizer.Add(self.pdfviewer, 6, wx.ALL|wx.EXPAND, 10)
        pdfpanel_sizer.Add(self.buttonpanel, 1, wx.EXPAND, 0)
        self.pdfpanel.SetSizer(pdfpanel_sizer)

        buttonpanel2_sizer.Add(self.revertbutton, 0, wx.ALL, 10)
        buttonpanel2_sizer.Add(self.donebutton, 0, wx.ALL, 10)
        self.buttonpanel2.SetSizer(buttonpanel2_sizer)

        editorpanel_sizer.Add(self.raweditor, 6, wx.ALL|wx.EXPAND, 10)
        editorpanel_sizer.Add(self.buttonpanel2, 1, wx.EXPAND, 0)
        self.editorpanel.SetSizer(editorpanel_sizer)

        self.mainpanel.SetSizer(mainsizer)

        rootsizer.Add(self.mainpanel, 1, wx.EXPAND, 0)

        self.SetSizer(rootsizer)
        rootsizer.Fit(self)

        self.SetSize((1000, 800))
        
        self.Layout()
        # end wxGlade


    def ondone(self):
        """"""
        self.EndModal(wx.ID_OK)
        
    def prev_page(self, event): # wxGlade: Frame.<event_handler>
        print "Event handler `prev_page' not implemented!"
        event.Skip()

        

class PDFWindow(wx.ScrolledWindow):
    """pdf viewer window. Taken from
    http://code.activestate.com/recipes/577195-wxpython-pdf-viewer-using-poppler/"""

    MAX_SCALE = 2
    MIN_SCALE = 1
    SCROLLBAR_UNITS = 20  # pixels per scrollbar unit

    def __init__(self, parent):
        wx.ScrolledWindow.__init__(self, parent, wx.ID_ANY)
        # Wrap a panel inside
        self.panel = wx.Panel(self)
        # Initialize variables
        self.n_page = 0
        self.scale = 1
        self.document = None
        self.n_pages = None
        self.current_page = None
        self.width = None
        self.height = None
        # Connect panel events
        self.panel.Bind(wx.EVT_PAINT, self.OnPaint)
        self.panel.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.panel.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.panel.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)

        #self.LoadDocument('/tmp/tmpLSvo1m.pdf')

    def LoadDocument(self, file):
        self.document = poppler.document_new_from_file("file://" + file, None)
        self.n_pages = self.document.get_n_pages()
        self.current_page = self.document.get_page(self.n_page)
        self.width, self.height = self.current_page.get_size() 
        self._UpdateSize()

    def OnPaint(self, event):
        dc = wx.PaintDC(self.panel)
        cr = wxcairo.ContextFromDC(dc)
        cr.set_source_rgb(1, 1, 1)  # White background
        if self.scale != 1:
            cr.scale(self.scale, self.scale)
            
        try:
            cr.rectangle(0, 0, self.width, self.height)
        except TypeError:
            cr.rectangle(0, 0, 680, 400)
            
        cr.fill()

        if self.current_page:
            self.current_page.render(cr)

    def OnLeftDown(self, event):
        self._UpdateScale(self.scale + 0.2)

    def OnRightDown(self, event):
        self._UpdateScale(self.scale - 0.2)

    def _UpdateScale(self, new_scale):
        if new_scale >= PDFWindow.MIN_SCALE and new_scale <= PDFWindow.MAX_SCALE:
            self.scale = new_scale
            # Obtain the current scroll position
            prev_position = self.GetViewStart() 
            # Scroll to the beginning because I'm going to redraw all the panel
            self.Scroll(0, 0) 
            # Redraw (calls OnPaint and such)
            self.Refresh() 
            # Update panel Size and scrollbar config
            self._UpdateSize()
            # Get to the previous scroll position
            self.Scroll(prev_position[0], prev_position[1]) 

    def _UpdateSize(self):
        u = PDFWindow.SCROLLBAR_UNITS
        self.panel.SetSize((self.width*self.scale, self.height*self.scale))
        self.SetScrollbars(u, u, (self.width*self.scale)/u, (self.height*self.scale)/u)

    def OnKeyDown(self, event):
        update = True
        # More keycodes in http://docs.wxwidgets.org/stable/wx_keycodes.html#keycodes
        keycode = event.GetKeyCode() 
        if keycode in (wx.WXK_PAGEDOWN, wx.WXK_SPACE):
            next_page = self.n_page + 1
        elif keycode == wx.WXK_PAGEUP:
            next_page = self.n_page - 1
        else:
            update = False
        if update and (next_page >= 0) and (next_page < self.n_pages):
            self.n_page = next_page
            self.current_page = self.document.get_page(next_page)
            self.Refresh()

    
    

if __name__ == '__main__':
    #editor_test()
    pass
