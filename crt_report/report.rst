
<%
    def get(item):
        """get from dict. Else return empty string."""
	try:
	    return vals[item] 
	except KeyError:
	    return ''
%>

<%
    def get_quoted(item):
        """get from dict. Else return empty string. Quote returned string"""
	try:
	    val = vals[item]
	except KeyError:
	    return ''
	if val.strip() == '':
	    return ''
	else:
	    return '"' + vals[item] + '"'

%>

<%
    def list2line(lst):
        """convert items in python list to a single line"""
	return ', '.join([x for x in lst if x.strip() != ''])	
%>


<%
    def list2onecolcsv(lst):
        """convert items in python list to a single column csv table"""
	return '\n    '.join([',"' + x + '"' for x in lst if x.strip() != ''])	
%>


<%
    def list2twocolcsv(lst):
        """convert list of strings to two col csv table.
	In each pair of strings, first is field and second is value"""
	pairs = zip(lst[::2], lst[1::2])
	non_empty_pairs = [pair for pair in pairs if pair[1].strip() != '']
	pair_strings = [''.join(('**', a, '**,', b)) for (a,b) in non_empty_pairs]
	return '\n    '.join(pair_strings)
%>


<%
    def noblanks(lst):
        """
	Given list of 3-tuples, for each tuple, join as string if
	middle element is not empty. Return final joined string
	within quotes
	"""
        lst = [pre+var+post  if var.strip() != '' else '' for (pre, var, post) in lst]
	# strip empty strings
	lst = [s for s in lst if s != '']
	
	if len(lst) == 0:
	    return ''
	else:
	    return '"' + ', '.join(lst) + '"'
%>


<%
    def invert_date(dt):
        """invert from yyyy-mm-dd to dd-mm-yyyy"""
	if dt == '':
	    return ''
	yr, mth, day = dt.split('-')
	return '-'.join([day, mth, yr])
%>	



|jipmer| Pacemaker implant discharge Summary
============================================

Department of Cardiology
------------------------

Jawaharlal Institute of Postgraduate Medical Education and Research
--------------------------------------------------------------------

.. csv-table:: Demographics
   :widths: 3, 2, 3, 2, 3, 2

          "**Name**", ${get_quoted('Demographics_Name')}, "**Age**", ${get_quoted('Demographics_Age')}, "**Sex**", ${get_quoted('Demographics_Sex')}
	  "**IP No.**", ${get_quoted('Demographics_IP Number')}, "**MRD No.**", ${get_quoted('Demographics_MRD Number')}, "**Procedure No**", ${get_quoted('Demographics_Procedure No')}
	 "**Start time**", ${get_quoted('Demographics_Procedure Start')}, "**End time**", ${get_quoted('Demographics_Procedure End')}, "**Fluoro time**", ${get_quoted('Demographics_Fluoro time')}
	 "**Operator 1**", ${get_quoted('Procedure_Operator 1')}, "**Operator 2**", ${get_quoted('Procedure_Operator 2')}, "**Tech**", ${get_quoted('Procedure_Technician')}
	 "**Date of Admission**", ${invert_date(get('Demographics_Date of Admission'))}, "**Date of Procedure**", ${invert_date(get('Demographics_Date of Procedure'))}, "**Date of Discharge**", ${invert_date(get('Demographics_Date of Discharge'))}  

.. csv-table:: Procedure
   :widths: 3, 10

   "**Indication for procedure**", ${get('Preop diagnosis 1')} + ${get('Preop diagnosis 2')} + ${get('Preop diagnosis 3')} 
   "**Procedure performed**", ${get('Procedure_Procedure 1')} + ${get('Procedure_Procedure 2')} + ${get('Procedure_Procedure 3')}

   
.. csv-table:: Baseline investigations

   "**Hb**", ${get('Investigations_Hb')}, "**TC**", ${get('Investigations_TC')}, "**DC**", ${get('Investigations_DC')}
   "**Urea**", ${get('Investigations_Bld Urea')}, "**Creatinine**", ${get('Investigations_Se Creat')}, "**B Sugar**", ${get('Investigations_Bld Sugar')}
   "**HIV**", ${get('Investigations_HIV')}, "**HBsAg**", ${get('Investigations_HBsAg')}, "**HCV** ", ${get('Investigations_HCV')}


Procedure details
~~~~~~~~~~~~~~~~~
% if 'pacemaker implant' in vals['Procedure_Procedure 1']:

Under ${get('Procedure_Anaesthesia')}, an incision was made in the ${get('Procedure_Side')} ${get('Procedure_Incision')} region. Venous access was obtained by ${get('Procedure_Venous Access 1')}. A ${get('New Lead 1_Polarity')} ${get('New Lead 1_Fixation')} fixation lead was positioned in the ${get("New Lead 1_Position")}. A ${get('Pulse Generator_Source')} ${get('Pulse Generator_Model')} with serial no: ${get('Pulse Generator_Serial no.')} was connected to the lead and placed in a ${get("Procedure_Pocket")} pocket. Lead parameters are mentioned below. Gentamicin was instilled locally. After securing hemostasis, subcutaneous tissue was closed with ${get("Procedure_Subcutaneous closure")} sutures and skin was closed with ${get("Procedure_Skin closure")} sutures.

% endif


% if "${get_quoted('Procedure_Procedure')}" == "Pulse generator change":

Under (Anaesthesia), an incision was made over the pulse generator and this was explanted. The leads were disconnected the the parameters are as mentioned below. A (Pulse Generator Source) (Pulse Generator Model) pacemaker was attached to the lead and placed back in the pocket. Gentamicin was instilled locally. After securing hemostasis, subcutaneous tissue was closed with (Procedure Subcutaneous closure) sutures and skin was closed with (Procedure Skin closure) sutures.

% endif

.. class:: heading-table
.. csv-table:: Lead Parameters
   :header-rows: 1
   :widths: 4, 10, 10, 8, 6, 6, 6, 6, 8
   
   "", "**Position**", "**Type** (Polarity, Fixation)", "**Model**", "**Sl**", "**Imp**", "**Ampl**", "**Thresh**", "**Date of Implant**"
   "1", "", "", "", "", "", "", "", ""
   "2",   "", "", "", "", "", "", "", ""


.. csv-table:: Final Settings

   "**Mode**", " ", "**Lower Rate**", " ", "**AV delay**",""
   "**RA ouput**","", "**RV output**","", "**LV output**",""


.. raw:: pdf

       Spacer 0 20


Recommendations
~~~~~~~~~~~~~~~
  - Keep wound clean and dry.
  - Avoid excessive arm movements for 6 weeks
  - Review after 6 weeks in the Cardiology OPD (184) on Wednesday at 02.30 pm


.. raw:: pdf

       Spacer 0 40
     
    
| **Dr. Raja J. Selvaraj**
| **Assistant Professor of Cardiology**
| **JIPMER**

      
     
.. |jipmer| image:: {{jipmer_logo.png}}
                  :height: 1in
                  :width: 1in
	    	  :align: middle

.. footer::

   Page ###Page### 
