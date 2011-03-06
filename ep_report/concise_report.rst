<%
    def get(item):
        """get from dict. Else return empty string."""
	try:
	    return vals[item]
	except KeyError:
	    return ''
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
    def noblanks(pre, var, post):
        """If var is not empty string, return pre+var+post.
	Else return empty string"""
	if var.strip() == '':
            return ''
	else:
	    return ''.join([pre, var, post])
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

          "**Name**", "${get('Demographics_Name')}", "**Age**", "${get('Demographics_Age')} yrs", "**Sex**", "${get('Demographics_Sex')}"
	  "**Date of Adm.**", "${invert_date(get('Demographics_Date of Admission'))}", "**Proc. date**", "${invert_date(get('Demographics_Date of Procedure'))}", "**Contact No.**", "${get('Demographics_Contact number')}"
	  "**IP No.**", "${get('Demographics_IP Number')}", "**MRD No.**", "${get('Demographics_MRD Number')}", "**EPS No.**", "${get('Demographics_EPS Number')}"
	  "**Lab**", "${get('Technical_Lab')}", "**EP System**", "${get('Technical_EP System')}", "**3 D mapping**", "${get('Technical_3D Mapping')}"
	  "**Operator 1**", "${get('Technical_Operator 1')}", "**Operator 2**", "${get('Technical_Operator 2')}", "**Tech. Asst**", "${get('Technical_Technical Assistant')}"
	  "**Procedure start**", "${get('Demographics_Procedure Start')}", "**Procedure end**", "${get('Demographics_Procedure End')}", "**Fluoro time**", "${get('Demographics_Fluoro time')} mins"

.. csv-table:: Clinical
   :widths: 3, 10

    "**Presentation**", "${get('Clinical_Presentation')}"
    "**ECG**", "${get('Clinical_ECG')}"
    "**ECG during tachy**", "${get('Clinical_ECG during tachycardia')}"
    "**Other inv**", "${get('Clinical_Other investigations')}"
    "**Drugs**", "${get('Clinical_Drugs')}"

.. csv-table:: Investigations

   "**Hb**", "${get('Investigations_Hb')} gms/dl", "**Bld Sugar**", "${get('Investigations_Bld Sugar')} mg/dl", "**Bld Urea**", "${get('Investigations_Bld Urea')} mg/dl"
   "**Se Creatinine**", "${get('Investigations_Se Creat')}",  "**HIV**", "${get('Investigations_HIV')}", "**HBsAg**", "${get('Investigations_HBsAg')}"
    

.. csv-table:: Access and catheters
   :widths: 3, 10

    "**Access**", "${list2line([get('Technical_Access 1'), get('Technical_Access 2'),get('Technical_Access 3'), get('Technical_Access 4')])}"
    "**Catheters**", "${list2line([get('Technical_Catheter 1'), get('Technical_Catheter 2'),
                                   get('Technical_Catheter 3'), get('Technical_Catheter 4'),
				   get('Technical_Catheter 5')])}"


.. csv-table:: Baseline
   :widths: 3, 10

   "**Rhythm**", "${get('Baseline_Rhythm')}"
   "**Measurements**", "${noblanks('PR ', get('Baseline_PR'), ' ms,')} ${noblanks('AH ', get('Baseline_AH'), ' ms,')} ${noblanks('HV ', get('Baseline_HV'), ' ms')}, CL ${get('Baseline_CL')}ms"
   "**ParaHisian pacing**", "${get('Baseline_Parahisian')}"
   "**Incr RV pace**", "VA conduction ${get('Incr V Pace_VA conduction')}, VAWB ${get('Incr V Pace_VAWB')}ms, Atrial activation ${get('Incr V Pace_Atrial Activation')}"
   "**Progr RV pace**", "VA conduction ${get('Prog V Pace_VA conduction')}, VAERP ${get('Prog V Pace_VAERP')}ms, Atrial activation ${get('Prog V Pace_Atrial Activation')}, VERP ${get('Prog V Pace_VERP')}ms"
    "**Incr A pace**", "AVWB ${get('Incr A Pace_AVWB')} ms, Level of block ${get('Incr A Pace_Level of block')}, PR>RR ${get('Incr A Pace_PR>RR')}"
    "**Prog A pace**", "AH jump ${get('Prog A Pace_AH jump')} ms, ${noblanks('FPERP ',get('Prog A Pace_FPERP'), ' ms,')} ${noblanks('SPERP ',get('Prog A Pace_SPERP'), ' ms,')}  ${noblanks('APERP ', get('Prog A Pace_APERP'), ' ms,')} ${noblanks('AVERP ', get('Prog A Pace_AVERP'), ' ms,')} ${noblanks ('AERP ', get('Prog A Pace_AERP'),' ms')}."


.. csv-table:: Tachycardia
   :widths: 3, 10

    "**Induction**", "${get('Tachycardia_Induction')}, ${get('Tachycardia_Termination')}"
    "**Measurements**", "${get('Tachycardia_QRS')} tachycardia, CL ${get('Tachycardia_CL')}ms, ${noblanks('AH ',get('Tachycardia_AH'), ' ms,')} ${noblanks('HV ',get('Tachycardia_HV'), ' ms,')} ${noblanks('VA ',get('Tachycardia_VA'), ' ms')}"
    "**VA relation**", "${get('Tachycardia_VA relationship')} with ${get('Tachycardia_Atrial activation')}"
    "**RV Pacing**", "${get('Tachycardia_RV overdrive')} ${noblanks(', RV extra - ',get('Tachycardia_RV extra'), '.')}"
    "**Atrial Pacing**", "${get('Tachycardia_RA overdrive')} ${noblanks(', ', get('Tachycardia_RA extra'), '.')}"
    "**Comment**", "${get('Tachycardia_Comment')}"



.. csv-table:: Mapping and RF ablation
    :widths: 3, 10

    "**Catheter**", "${get('Ablation_Catheter')}"
    "**Approach**", "${get('Ablation_Approach')}"
    "**Target**", "${get('Ablation_Target')}"
    "**RF**", "Settings - ${get('Ablation_Settings')}, RF applications - ${get('Ablation_RF applications')}, RF time - ${get('Ablation_Time')} seconds"
    "**Endpoint**", "${get('Ablation_Endpoint')}"
    "**Comments**", "${get('Ablation_Comments')}"


.. csv-table:: Post ablation
   :widths: 5, 8, 5, 8

      "**Measurements**", "${get('Post Ablation_Rhythm')}, CL ${get('Post Ablation_CL')}ms, AH ${get('Post Ablation_AH')}, HV ${get('Post Ablation_HV')}", "**ParaHisian pacing**", "${get('Post Ablation_Parahisian')}"
    "**Incr RV pace**", "${get('Post Ablation_Incr V Pace')}",     "**Prog RV pace**", "${get('Post Ablation_Prog V Pace')}"
    "**Incr A pace**", "${get('Post Ablation_Incr A Pace')}", "**Prog A pace**", "${get('Post Ablation_Prog A Pace')}"
    "**Comments**", "${get('Post Ablation_Comments')}", "", ""
    

.. csv-table:: Conclusions
   :widths: 1, 50

     ${list2onecolcsv([get('Conclusions_Conclusion 1'),
                    get('Conclusions_Conclusion 2'),
		    get('Conclusions_Conclusion 3'),
		    get('Conclusions_Conclusion 4')])}

     
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

       
     
.. |jipmer| image:: /data/Dropbox/programming/EP_report2/ep_report/jipmer_logo.png
              :height: 1in
    	      :width: 1in
	      :align: middle

.. footer::

   EP report  Pg.###Page###
	      
