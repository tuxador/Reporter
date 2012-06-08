
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



|jipmer| Biventricular Pacemaker Implant Report
===============================================

Department of Cardiology
------------------------

Jawaharlal Institute of Postgraduate Medical Education and Research
--------------------------------------------------------------------

.. csv-table:: Demographics
   :widths: 2, 2,2 , 2, 2, 2

          "**Name**", ${get_quoted('Demographics_Name')}, "**Age**", ${get_quoted('Demographics_Age')} yrs, "**Sex**", ${get_quoted('Demographics_Sex')}
	  "**IP No.**", ${get_quoted('Demographics_IP Number')}, "**MRD No.**", ${get_quoted('Demographics_MRD Number')}, "**Procedure No.**", ${get_quoted('Demographics_Procedure No')}
	 "**Start time**", ${get_quoted('Demographics_Procedure Start')}, "**End time**", ${get_quoted('Demographics_Procedure End')}, "**Fluoro time**", ${get_quoted('Demographics_Fluoro time')} min
	 "**Operator 1**", ${get_quoted('Procedure_Operator 1')}, "**Operator 2**", ${get_quoted('Procedure_Operator 2')}, "**Tech**", ${get_quoted('Procedure_Technician')}
	 "**Admission**", ${invert_date(get('Demographics_Date of Admission'))}, "**Procedure**", ${invert_date(get('Demographics_Date of Procedure'))}, "**Discharge**", ${invert_date(get('Demographics_Date of Discharge'))}  


   
.. csv-table:: Baseline investigations

   "**Hb**", ${get('Investigations_Hb')} g/dl, "**TC**", ${get('Investigations_TC')}, "**DC**", ${get('Investigations_DC')}
   "**Urea**", ${get('Investigations_Bld Urea')} mg/dl, "**Creatinine**", ${get('Investigations_Se Creat')} mg/dl, "**B Sugar**", ${get('Investigations_Bld Sugar')} mg/dl
   "**HIV**", ${get('Investigations_HIV')}, "**HBsAg**", ${get('Investigations_HBsAg')}, "**HCV** ", ${get('Investigations_HCV')}


Indication for procedure
~~~~~~~~~~~~~~~~~~~~~~~~
${get('Clinical_Heart failure etiology')} with LVEF ${get('Clinical_LVEF')}%,  congestive heart failure NYHA class ${get('Clinical_NYHA Class')}, ${get('Clinical_QRS morphology')} in ECG with QRS width ${get('Clinical_QRS width')} ms. ${get('Clinical_Comments')}
   

Procedure details
~~~~~~~~~~~~~~~~~
% if 'New CRT implant' in vals['Procedure_Procedure 1']:

Under ${get('Procedure_Anaesthesia')}, an incision was made in the ${get('Procedure_Side')} ${get('Procedure_Incision')} region. Through a ${get('Procedure_Access for RV lead')}, a ${get('Ventricular lead_Polarity')} ${get('Ventricular lead_Fixation')} fixation lead was positioned in the ${get('Ventricular lead_Position')}. Through a ${get('Procedure_Access for LV lead')}, a ${get('Procedure_Long sheath')} long sheath was placed through a 9F short sheath. Coronary sinus was cannulated using the long sheath with ${get('Procedure_CS cannulation')}. ${get('Procedure_Venogram findings')}.
% if vals['Procedure_Lead positioning technique'] == 'over wire':
A 0.014 inch guidewire was used to cannulate the selected branch and the coronary sinus pacing lead was positioned over the wire. 
% endif
The long sheath was ${get('Procedure_Long sheath removal')} and removed. Subsequently, through a ${get('Procedure_Access for RA lead')}, a ${get('Atrial lead_Polarity')} ${get('Atrial lead_Fixation')} fixation lead was positioned in the ${get('Atrial lead_Position')}. A ${get('Pulse Generator_Model')} biventricular pacemaker was connected to the leads and placed in a ${get("Procedure_Pocket")} pocket. Lead parameters are mentioned below. Gentamicin was instilled locally. After securing hemostasis, subcutaneous tissue was closed with ${get("Procedure_Subcutaneous closure")} sutures and skin was closed with ${get("Procedure_Skin closure")} sutures.

% endif


% if "${get_quoted('Procedure_Procedure')}" == "Pulse generator change":

Under (Anaesthesia), an incision was made over the pulse generator and this was explanted. The leads were disconnected the the parameters are as mentioned below. A (Pulse Generator Source) (Pulse Generator Model) pacemaker was attached to the lead and placed back in the pocket. Gentamicin was instilled locally. After securing hemostasis, subcutaneous tissue was closed with (Procedure Subcutaneous closure) sutures and skin was closed with (Procedure Skin closure) sutures.

% endif

.. class:: heading-table
.. csv-table:: Lead Parameters
   :header-rows: 1
   :widths: 4,8,6,6,12,8,5,5,5
	    
    "", "**Position**", "**Polarity**", "**Fixation**", "**Model**", "**Sl no.**", "**Imp** (Ohms)", "**Ampl** (mV)", "**Thresh** (V/0.5 ms)"
   "RA", ${get('Atrial lead_Position')}, ${get('Atrial lead_Polarity')}, ${get('Atrial lead_Fixation')}, ${get('Atrial lead_Model')}, ${get('Atrial lead_Serial no.')}, ${get('Atrial lead_Impedance')}, ${get('Atrial lead_Sensing amplitude')}, ${get('Atrial lead_Pacing Threshold')}
   "RV", ${get('Ventricular lead_Position')}, ${get('Ventricular lead_Polarity')}, ${get('Ventricular lead_Fixation')}, ${get('Ventricular lead_Model')}, ${get('Ventricular lead_Serial no.')}, ${get('Ventricular lead_Impedance')}, ${get('Ventricular lead_Sensing amplitude')}, ${get('Ventricular lead_Pacing Threshold')}
   "CS", ${get('CS lead_Position')}, ${get('CS lead_Polarity')}, ${get('CS lead_Fixation')}, ${get('CS lead_Model')}, ${get('CS lead_Serial no.')}, ${get('CS lead_Impedance')}, ${get('CS lead_Sensing amplitude')}, ${get('CS lead_Pacing Threshold')}



.. csv-table:: Final Settings

   "**Mode**", ${get('Settings_Mode')}, "**Lower Rate** (bpm)", ${get('Settings_Lower Rate')}, "**SAV delay** (ms)", ${get('Settings_SAV delay')}, "**PAV delay**", ${get('Settings_PAV delay')}
   "**LV/RV offset** (ms)", ${get('Settings_LV to RV offset')}, "**RA output** (V/ms)", ${get('Settings_RA output')}, "**RV output** (V/ms)", ${get('Settings_RV output')}, "**LV output** (V/ms)", ${get('Settings_LV output')}


.. raw:: pdf

       Spacer 0 20


.. csv-table:: Recommendations
   :widths: 1, 50

      ${list2onecolcsv([get('Recommendations_Recommendation 1'),
                    get('Recommendations_Recommendation 2'),
		    get('Recommendations_Recommendation 3'),
		    get('Recommendations_Recommendation 4')])}


.. csv-table:: Medications at discharge
   :widths: 1, 50

     ${list2onecolcsv([get('Medications_Drug 1'),
                      get('Medications_Drug 2'),
                      get('Medications_Drug 3'),
                      get('Medications_Drug 4'),
                      get('Medications_Drug 5'),
                      get('Medications_Drug 6'),
                      get('Medications_Drug 7'),
		      get('Medications_Drug 8'),
                      get('Medications_Drug 9')])}
    

.. raw:: pdf

       Spacer 0 40
     
    
| **Dr. Raja J. Selvaraj MD DNB (Cardio) FICE (Toronto)**
| **Cardiac Electrophysiologist**
| **Assistant Professor of Cardiology**
| **JIPMER**

      
     
.. |jipmer| image:: {{jipmer_logo.png}}
                  :height: 1in
                  :width: 1in
	    	  :align: middle

.. footer::

   Page ###Page### of ###Total###
