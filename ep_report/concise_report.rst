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


|jipmer|  Electrophysiology study and RF ablation
=================================================

Department of Cardiology
------------------------

Jawaharlal Institute of Postgraduate Medical Education and Research
--------------------------------------------------------------------

Puducherry - 605006
-------------------

.. csv-table:: Demographics

          "**Name**", "${get('Demographics_Name')}", \
	       "**Age**", "${get('Demographics_Age')} yrs", \
	       "**Sex**", "${get('Demographics_Sex')}"
	  "**Date of Adm.**", "${invert_date(get('Demographics_Date of Admission'))}", \
	       "**Proc. date**", "${invert_date(get('Demographics_Date of Procedure'))}", \
	       "**Date of Disch.**", ""
	  "**IP No.**", "${get('Demographics_IP Number')}", \
	       "**MRD No.**", "${get('Demographics_MRD Number')}", \
	       "**EPS No.**", "${get('Demographics_EPS Number')}"
	  "**Lab**", "${get('Technical_Lab')}", \
	       "**EP System**", "${get('Technical_EP System')}", \
	       "**3 D mapping**", "${get('Technical_3D Mapping')}"
	  "**Operator 1**", "${get('Technical_Operator 1')}", \
	       "**Operator 2**", "${get('Technical_Operator 2')}", \
	       "**Tech. Asst**", "${get('Technical_Technical Assistant')}"
	  "**Procedure start**", "${get('Demographics_Procedure Start')}", \
	       "**Procedure end**", "${get('Demographics_Procedure End')}", \
	       "**Fluoro time**", "${get('Demographics_Fluoro time')} mins"

.. csv-table:: Clinical
   :widths: 3, 10

   ${list2twocolcsv(['Presentation', get_quoted('Clinical_Presentation'),
                     'ECG', get_quoted('Clinical_ECG'),
		     'ECG during tachy', get_quoted('Clinical_ECG during tachycardia'),
		     'Other inv', get_quoted('Clinical_Other investigations'),
		     'Drugs', get_quoted('Clinical_Drugs') ])}


.. csv-table:: Investigations

   "**Hb**", "${get('Investigations_Hb')} gms/dl", \
        "**Bld Sugar**", "${get('Investigations_Bld Sugar')} mg/dl", \
	"**Bld Urea**", "${get('Investigations_Bld Urea')} mg/dl"
   "**Se Creatinine**", "${get('Investigations_Se Creat')}",  \
        "**HIV**", "${get('Investigations_HIV')}", \
        "**HBsAg**", "${get('Investigations_HBsAg')}"
    

.. csv-table:: Access and catheters
   :widths: 3, 10

    "**Access**", "${list2line([get('Technical_Access 1'), \
                                get('Technical_Access 2'), \
				get('Technical_Access 3'), \
				get('Technical_Access 4')])}"
    "**Catheters**", "${list2line([get('Technical_Catheter 1'), \
                                   get('Technical_Catheter 2'), \
                                   get('Technical_Catheter 3'), \
				   get('Technical_Catheter 4'), \
				   get('Technical_Catheter 5')])}"

				   
.. csv-table:: Baseline
   :widths: 3, 10

   ${list2twocolcsv(['Rhythm', get_quoted('Baseline_Rhythm'),
      'Measurements', noblanks([ ('PR ', get('Baseline_PR'), ' ms'),
                              ('AH ', get('Baseline_AH'), ' ms'),
			      ('HV ', get('Baseline_HV'), ' ms'),
			      ('CL ', get(', Baseline_CL'), 'ms')]),
      'Incr RV pace', noblanks([ ('VA conduction ', get('Incr V Pace_VA conduction'), ''),
                              ('VAWB ', get('Incr V Pace_VAWB'), ' ms'),
			      ('atrial activation ',get('Incr V Pace_Atrial Activation'), '')]),
      'Progr RV pace', noblanks([('VA conduction ', get('Prog V Pace_VA conduction'), ''),
                              ('VAERP ', get('Prog V Pace_VAERP'), ' ms'),
			      ('atrial activation ',get('Prog V Pace_Atrial Activation'), ''),
			      ('VERP ', get('Prog V Pace_VERP'), ' ms')]), 
      'Comment', get_quoted('Baseline_Comments')])}



.. csv-table:: Tachycardia
   :widths: 3, 10

   ${list2twocolcsv(['Induction', noblanks([('', get('Tachycardia_Induction'), ''),
                                            ('', get('Tachycardia_Termination'), '')]),
       'Measurements', noblanks([('', get('Tachycardia_QRS'), ' tachycardia'),
                                 ('CL ', get('Tachycardia_CL'), ' ms'),
				 ('AH ', get('Tachycardia_AH'), ' ms'),
				 ('HV ', get('Tachycardia_HV'), ' ms' ),
				 ('VA ', get('Tachycardia_VA'), ' ms')]),
       'VA relation', noblanks([('VA relation ', get('Tachycardia_VA relationship'), ''),
                                ('atrial activation ', get('Tachycardia_Atrial activation'), '')]),
       'RV Pacing', noblanks([('', get('Tachycardia_RV overdrive'), ''),
                              ('RV extra - ', get('Tachycardia_RV extra'), '')]),
       'Atrial Pacing', noblanks([('', get('Tachycardia_RA overdrive'), ''),
                                  ('', get('Tachycardia_RA extra'), '')]),
       'Comment', get_quoted('Tachycardia_Comment')])}



.. csv-table:: Mapping and RF ablation
    :widths: 3, 10

    ${list2twocolcsv(['Catheter', get_quoted('Ablation_Catheter'),
                      'Approach', get_quoted('Ablation_Approach'),
    		      'Target', get_quoted('Ablation_Target'),
		      'RF', noblanks([('Settings - ', get('Ablation_Settings'), ''),
		                      ('RF applications - ', get('Ablation_RF applications'), '' ),
				      ('RF time - ', get('Ablation_Time'), ' seconds')]),
                      'Endpoint', get_quoted('Ablation_Endpoint'),
		      'Comments', get_quoted('Ablation_Comments')])}


.. csv-table:: Post ablation
   :widths: 3, 10

   ${list2twocolcsv(['Measurements', noblanks([('Rhythm ', get('Post Ablation_Rhythm'), ''),
                                               ('CL ', get('Post Ablation_CL'), ' ms'),
					       ('AH ', get('Post Ablation_AH'), ' ms'),
					       ('HV ', get('Post Ablation_HV'), ' ms')]),
                     'ParaHisian pacing', get_quoted('Post Ablation_Parahisian'),
		     'Incr RV pace', get_quoted('Post Ablation_Incr V Pace'),
		     'Prog RV pace', get_quoted('Post Ablation_Prog V Pace'),
		     'Incr A pace', get_quoted('Post Ablation_Incr A Pace'),
		     'Prog A pace', get_quoted('Post Ablation_Prog A Pace'),
		     'Comments', get_quoted('Post Ablation_Comments')])}
    

.. csv-table:: Conclusions
   :widths: 1, 50

     ${list2onecolcsv([get('Conclusions_Conclusion 1'),
                    get('Conclusions_Conclusion 2'),
		    get('Conclusions_Conclusion 3'),
		    get('Conclusions_Conclusion 4'),		    
		    get('Conclusions_Conclusion 5')])}

     
.. csv-table:: Recommendations
   :widths: 1, 50




      ${list2onecolcsv([get('Recommendations_Recommendation 1'),
                    get('Recommendations_Recommendation 2'),
		    get('Recommendations_Recommendation 3'),
		    get('Recommendations_Recommendation 4')])}


.. raw:: pdf

       Spacer 0 40
     


| Dr. Raja Selvaraj  
| Assistant Professor of Cardiology
| JIPMER

       
     
.. |jipmer| image:: {{jipmer_logo.png}}
              :height: 1in
    	      :width: 1in
	      :align: middle

.. footer::

   EP report  Pg.###Page###
	      
       

