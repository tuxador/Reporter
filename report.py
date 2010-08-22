#!/usr/bin/env python

"""Use supplied dictionary of values and a template to fill in the template
with mako and render the report to a pdf with rst2pdf"""

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
        tmp_rstfilename = tempfile.mkstemp(suffix='rst')[1]
        tmp_pdffilename = tempfile.mkstemp(suffix='pdf')[1]

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
        pass




    

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
    



if __name__ == '__main__':
    test()
