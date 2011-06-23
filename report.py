#!/usr/bin/env python

"""Use supplied dictionary of values and a template to fill in the template
with mako and render the report to a pdf with rst2pdf"""

import wx
#import subprocess
import time
import shutil

import tempfile
from mako.template import Template
#from rst2pdf.createpdf import RstToPdf
from rst2pdf import createpdf

if wx.Platform == '__WXMSW__':
    from wx.lib.pdfwin import PDFWindow

elif wx.Platform == '__WXGTK__':
    import wx.lib.wxcairo as wxcairo
    import poppler    

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

        # flag to indicate if stored raw report is used
        self.STORED_RAW = False
        
        # create a new report only if there isnt one stored
        if self.raw_report == '':
            self.STORED_RAW = True
            self.generate_raw()

        print 'initing report with', self.raw_report
    

    def generate_raw(self, event=None):
        """fill the template to create a raw_report"""
        self.raw_report = self.template.render(vals=self.vals)
        

    def generate_pdf(self, raw=None):
        """Creat pdf and return path to pdf file.
        Use given rst text or use raw_report"""
        # get the temp names
        tmp_rstfilename = tempfile.mkstemp(suffix='.rst')[1]
        tmp_pdffilename = tempfile.mkstemp(suffix='.pdf')[1]

        #TODO: for debug only
        #tmp_pdffilename = 'F:/EP_report2/test.pdf'
        
        if not raw:
            raw = self.raw_report
        
        # write the raw_report as a file
        with open(tmp_rstfilename,'w') as fi:
            fi.write(raw)

        # invoke rst2pdf
        if self.stylefile:
            cmd = ['-s', self.stylefile, tmp_rstfilename, '-o', tmp_pdffilename]
        else:
            cmd = [tmp_rstfilename, '-o', tmp_pdffilename]

        createpdf.main(cmd)

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

        # custom statusbar
        self.statusbarpanel = wx.Panel(self, -1, size=((20,40)),
                                       style=wx.SUNKEN_BORDER)
        self.statusbar = wx.StaticText(self.statusbarpanel, -1, 'This is the statusbar')
        
        self.splitter = wx.SplitterWindow(self.mainpanel, -1, style=wx.SP_3D|wx.SP_BORDER)

        self.editorpanel = wx.Panel(self.splitter, -1)
        self.pdfpanel = wx.Panel(self.splitter, -1)
        self.splitter.SetMinimumPaneSize(20)

        self.buttonpanel = wx.Panel(self.pdfpanel, -1)
        self.buttonpanel2 = wx.Panel(self.editorpanel, -1)

        if wx.Platform == '__WXMSW__':
            self.pdfviewer = PDFWindowWin(self.pdfpanel)
        elif wx.Platform == '__WXGTK__':
            self.pdfviewer = PDFWindowLin(self.pdfpanel)
            
        self.raweditor = wx.TextCtrl(self.editorpanel, -1, "",
                                     style=wx.TE_MULTILINE)

        self.save_button = wx.Button(self.buttonpanel, -1, "Save pdf")
        self.print_button = wx.Button(self.buttonpanel, -1, "Print pdf")
        self.prev_button = wx.Button(self.buttonpanel, -1, "Prev Page")
        self.next_button = wx.Button(self.buttonpanel, -1, "Next Page")
        self.refresh_button = wx.Button(self.buttonpanel, -1, "Refresh")  
        self.editor_show_button = wx.Button(self.buttonpanel, -1, "Show Editor")
        
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
        self.Bind(wx.EVT_BUTTON, self.ondone, self.donebutton)
        self.Bind(wx.EVT_BUTTON, self.print_pdf, self.print_button)
        self.Bind(wx.EVT_BUTTON, self.save_pdf, self.save_button)
        self.Bind(wx.EVT_BUTTON, self.prev_page, self.prev_button)
        self.Bind(wx.EVT_BUTTON, self.next_page, self.next_button)
        self.Bind(wx.EVT_BUTTON, self.refresh_pdf, self.refresh_button)
        self.Bind(wx.EVT_BUTTON, self.show_editor, self.editor_show_button)


    def prev_page(self, event):
        self.pdfviewer.goto_prevpage()

    def next_page(self, event):
        self.pdfviewer.goto_nextpage()

    def print_pdf(self, event):
        pass #TODO:


    def save_pdf(self, event):
        """Save pdf by copying temp file"""
        dlg = wx.FileDialog(None, 'Save pdf as', style=wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK:
            savefile = dlg.GetPath()

        shutil.copyfile(self.pdf_file, savefile)
        
        
# end wxGlade
    def _init_values(self):
        """Initialise values in texteditor and pdf viewer"""
        self.pdf_file = self.report.generate_pdf()
        time.sleep(3)
        
        #self.show_message('Loaded pdf')
        if self.report.STORED_RAW == True:
            self.show_message('Using stored report')
        else:
            self.show_message('Creating new report')
        
        w, h = self.GetSize()
        self.splitter.SetSashPosition(h)
        self.EDITOR_SHOWN = False
        self.editor_show_button.SetLabel("Show Editor")

        self.raweditor.write(self.raw_text)
        #time.sleep(10)
        self.pdfviewer.load_file(self.pdf_file)
        #print 'pdf file name', self.pdf_file
        #self.pdfviewer.load_file('F:/EP_report2/ep_report/reports/arun.pdf')
        #self.pdfviewer.load_file('c:\docume~1\raja\locals~1\temp\tmpltu2dh.pdf')
        

    def refresh_pdf(self, event):
        """refresh the displayed pdf"""
        self.show_message('Refreshing pdf ...')
        time.sleep(1)
        self.pdf_file = self.report.generate_pdf(self.raweditor.GetValue())
        time.sleep(2)

        self.pdfviewer.load_file(self.pdf_file)
        self.pdfviewer.Refresh()
        self.show_message('Reloaded pdf')

    def __do_layout(self):
        # begin wxGlade: Frame.__do_layout
        rootsizer = wx.BoxSizer(wx.VERTICAL)

        statussizer = wx.BoxSizer(wx.VERTICAL)
        statussizer.Add(self.statusbar, 0, wx.ALL, 2)
        self.statusbarpanel.SetSizer(statussizer)
        
        mainsizer = wx.BoxSizer(wx.VERTICAL)
        editorpanel_sizer = wx.BoxSizer(wx.VERTICAL)
        buttonpanel2_sizer = wx.BoxSizer(wx.HORIZONTAL)
        pdfpanel_sizer = wx.BoxSizer(wx.VERTICAL)
        buttonpanel_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.splitter.SplitHorizontally(self.pdfpanel, self.editorpanel)
        mainsizer.Add(self.splitter, 1, wx.EXPAND, 0)

        buttonpanel_sizer.Add(self.save_button, 0, wx.ALL, 5)
        buttonpanel_sizer.Add(self.print_button, 0, wx.ALL, 5)
        buttonpanel_sizer.Add(self.prev_button, 0, wx.ALL, 5)
        buttonpanel_sizer.Add(self.next_button, 0, wx.ALL, 5)
        buttonpanel_sizer.Add(self.refresh_button, 0, wx.ALL, 5)
        buttonpanel_sizer.Add(self.editor_show_button, 0, wx.ALL, 5)
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

        rootsizer.Add(self.mainpanel, 12, wx.EXPAND, 0)
        rootsizer.Add(self.statusbarpanel, 1, wx.ALL|wx.EXPAND, 10)
        
        self.SetSizer(rootsizer)
        rootsizer.Fit(self)

        self.SetSize((600, 600))

        self.SetAutoLayout(True)
        #self.Layout()
        # end wxGlade


    def ondone(self, event):
        """"""
        self.EndModal(wx.ID_OK)
        

    def show_editor(self, event):
        """move the splitter sash to show the editor"""
        w,h = self.GetSize()
        
        if self.EDITOR_SHOWN:
            self.splitter.SetSashPosition(h)
            self.EDITOR_SHOWN = False
            self.editor_show_button.SetLabel("Show Editor")

        else:
            self.splitter.SetSashPosition(h/2)
            self.EDITOR_SHOWN = True
            self.editor_show_button.SetLabel("Hide Editor")

    def show_message(self, msg):
        """show the message in the statusbar"""
        self.statusbar.SetLabel(msg)
        

class PDFWindowWin(wx.Panel):
    """Adobe based pdf viewer for windows"""
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        #PDFWindow.__init__(self, style = wx.SUNKEN_BORDER)
        self.pdfwin = PDFWindow(self)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.pdfwin, 1, wx.EXPAND)
        self.SetSizer(sizer)
        
    def goto_prevpage(self):
        self.gotoPreviousPage()

    def goto_nextpage(self):
        self.gotoNextPage()

    def load_file(self, file):
        self.pdfwin.LoadFile(file)


        
class PDFWindowLin(wx.ScrolledWindow):
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
        self.panel.Bind(wx.EVT_PAINT, self.on_paint)
        self.panel.Bind(wx.EVT_KEY_DOWN, self.on_keydown)
        self.panel.Bind(wx.EVT_LEFT_DOWN, self.on_leftdown)
        self.panel.Bind(wx.EVT_RIGHT_DOWN, self.on_rightdown)

        #self.LoadDocument('/tmp/tmpLSvo1m.pdf')

    def load_file(self, file):
        self.document = poppler.document_new_from_file("file://" + file, None)
        self.n_pages = self.document.get_n_pages()
        self.current_page = self.document.get_page(self.n_page)
        self.width, self.height = self.current_page.get_size() 
        self._update_size()

    def on_paint(self, event):
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

    def on_leftdown(self, event):
        self._update_scale(self.scale + 0.2)

    def on_rightdown(self, event):
        self._update_scale(self.scale - 0.2)

    def _update_scale(self, new_scale):
        if new_scale >= PDFWindowLin.MIN_SCALE and new_scale <= PDFWindowLin.MAX_SCALE:
            self.scale = new_scale
            # Obtain the current scroll position
            prev_position = self.GetViewStart() 
            # Scroll to the beginning because I'm going to redraw all the panel
            self.Scroll(0, 0) 
            # Redraw (calls on_paint and such)
            self.Refresh() 
            # Update panel Size and scrollbar config
            self._update_size()
            # Get to the previous scroll position
            self.Scroll(prev_position[0], prev_position[1]) 

    def _update_size(self):
        u = PDFWindowLin.SCROLLBAR_UNITS
        self.panel.SetSize((self.width*self.scale, self.height*self.scale))
        self.SetScrollbars(u, u, (self.width*self.scale)/u, (self.height*self.scale)/u)

    def on_keydown(self, event):
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


    def goto_nextpage(self):
        """go to next page"""
        if self.n_page + 1 <= self.n_pages:
            self.n_page += 1
            self.current_page = self.document.get_page(self.n_page)
            self.Refresh()

        else:
            print 'Already at last page'
            return

    def goto_prevpage(self):
        """go to previous page"""
        if self.n_page > 0:
            self.n_page -= 1
            self.current_page = self.document.get_page(self.n_page)
            self.Refresh()

        else:
            print 'Already at first page'
            return

        

def test():
    """
    Primarily for debugging the pdf window problems on windows
    """
    app = wx.PySimpleApp()
    # create window/frame, no parent, -1 is default ID, title, size
    frame = wx.Frame(None, -1, "PDFWindow", size = (640, 480))
    # make an instance of the class
    panel = wx.Panel(frame)
    p = PDFWindowWin(panel)
    # show the frame
    mainsizer = wx.BOXSIZER(wx.VERTICAL)
    panelsizer = wx.BOXSIZER(wx.VERTICAL)

    panelsizer.Add(p, 1, wx.EXPAND)
    panel.SetSizer(panelsizer)

    mainsizer.Add(panel, 1, wx.EXPAND)
    frame.SetSizer(mainsizer)
    frame.SetAutoLayout(True)
    
    frame.Show(True)
    # start the event loop
    app.MainLoop()
    
    

if __name__ == '__main__':
    test()

