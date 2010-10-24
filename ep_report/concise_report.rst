

<%
    def list2line(lst):
        """convert items in python list to a single line"""
	return ', '.join([x for x in lst if x.strip() != ''])	
%>


<%
    def list2onecolcsv(lst):
        """convert items in python list to a single column csv table"""
	return '\n    '.join(["," + x for x in lst if x.strip() != ''])	
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




|jipmer|  Electrophysiology study and RF ablation
=================================================

Department of Cardiology
------------------------

Jawaharlal Institute of Postgraduate Medical Education and Research
--------------------------------------------------------------------


.. csv-table:: Demographics

          "**Name**", "${vals['Demographics_Name']}", "**Age**", "${vals['Demographics_Age']}", "**Sex**", "${vals['Demographics_Sex']}"
	  "**Date of Adm.**", "${vals['Demographics_Date of Admission']}", "**Proc. date**", "${vals['Demographics_Date of Procedure']}", "", ""
	  "**IP No.**", "${vals['Demographics_IP Number']}", "**Hospital No.**", "${vals['Demographics_Hospital Number']}", "**EPS No.**", "${vals['Demographics_EPS Number']}"
	  "**Lab**", "${vals['Technical_Lab']}", "**EP System**", "${vals['Technical_EP System']}", "**3 D mapping**", "${vals['Technical_3D Mapping']}"
	  "**Operator 1**", "${vals['Technical_Operator 1']}", "**Operator 2**", "${vals['Technical_Operator 2']}", "**Tech. Asst**", "${vals['Technical_Technical Assistant']}"
	  "**Procedure start**", "${vals['Demographics_Procedure Start']}", "**Procedure end**", "${vals['Demographics_Procedure End']}", "**Fluoro time**", "${vals['Demographics_Fluoro time']} mins"

.. csv-table:: Clinical
   :widths: 3, 10

    "**Presentation**", "${vals['Clinical_Presentation']}"
    "**ECG**", "${vals['Clinical_ECG']}"
    "**ECG during tachy**", "${vals['Clinical_ECG during tachycardia']}"
    "**Other inv**", "${vals['Clinical_Other investigations']}"
    "**Drugs**", "${vals['Clinical_Drugs']}"

.. csv-table:: Investigations

   "**Hb**", "${vals['Investigations_Hb']} gms/dl", "**Bld Sugar**", "${vals['Investigations_Bld Sugar']} mg/dl", "**Bld Urea**", "${vals['Investigations_Bld Urea']} mg/dl"
   "**HIV**", "${vals['Investigations_HIV']}", "**HBsAg**", "${vals['Investigations_HBsAg']}", "**HCV**", "${vals['Investigations_HCV']}"
    

.. csv-table:: Access and catheters
   :widths: 3, 10

    "**Access**", "${list2line([vals['Technical_Access 1'], vals['Technical_Access 2'],vals['Technical_Access 3'], vals['Technical_Access 4']])}"
    "**Catheters**", "${list2line([vals['Technical_Catheter 1'], vals['Technical_Catheter 2'],
                                   vals['Technical_Catheter 3'], vals['Technical_Catheter 4'],
				   vals['Technical_Catheter 5']])}"


.. csv-table:: Baseline
   :widths: 3, 10

   "**Measurements**", "AH ${vals['Baseline_AH']}ms, HV ${vals['Baseline_HV']}ms, CL ${vals['Baseline_CL']}ms"
   "**ParaHisian pacing**", "${vals['Baseline_Parahisian']}"
   "**Incr RV pace**", "VA conduction ${vals['Incr V Pace_VA conduction']}, VAWB ${vals['Incr V Pace_VAWB']}ms, Atrial activation ${vals['Incr V Pace_Atrial Activation']}"
   "**Progr RV pace**", "VA conduction ${vals['Prog V Pace_VA conduction']}, VAERP ${vals['Prog V Pace_VAERP']}ms, Atrial activation ${vals['Prog V Pace_Atrial Activation']}, VERP ${vals['Prog V Pace_VERP']}ms"
    "**Incr A pace**", "AVWB ${vals['Incr A Pace_AVWB']}, Level of block ${vals['Incr A Pace_Level of block']}, PR>RR ${vals['Incr A Pace_PR>RR']}"
    "**Prog A pace**", "AH jump ${vals['Prog A Pace_AH jump']}, SPERP ${vals['Prog A Pace_SPERP']}ms, FPERP ${vals['Prog A Pace_FPERP']}ms, AERP ${vals['Prog A Pace_AERP']}ms"

	 
	     

.. csv-table:: Tachycardia
   :widths: 3, 10


    "**Induction**", "${vals['Tachycardia_Induction']}, ${vals['Tachycardia_Termination']}"
    "**Measurements**", "${vals['Tachycardia_QRS']} tachycardia, CL ${vals['Tachycardia_CL']}ms, AH ${vals['Tachycardia_AH']}ms, HV ${vals['Tachycardia_HV']}ms, VA ${vals['Tachycardia_VA']}ms"
    "**VA relation**", "${vals['Tachycardia_VA relationship']} with ${vals['Tachycardia_Atrial activation']}"
    "**RV Pacing**", "${vals['Tachycardia_RV overdrive']}, ${noblanks('RV extra - ',vals['Tachycardia_RV extra'], '.')}"
    "**Atrial Pacing**", "${vals['Tachycardia_RA overdrive']}, ${vals['Tachycardia_RA extra']}"
    "**Comment**", "${vals['Tachycardia_Comment']}"

.. csv-table:: Mapping and RF ablation
    :widths: 4, 10, 4, 10

    "**Catheter**", "${vals['Ablation_Catheter']}", "**Target**", "${vals['Ablation_Target']}"
    "**Settings**", "${vals['Ablation_Settings']}",     "**Time**", "${vals['Ablation_Time']} seconds"
    "**Endpoint**", "${vals['Ablation_Endpoint']}", "**Comments**", "${vals['Ablation_Comments']}"


.. csv-table:: Post ablation
   :widths: 5, 8, 5, 8

      "**Measurements**", "${vals['Post Ablation_Rhythm']}, CL ${vals['Post Ablation_CL']}ms, AH ${vals['Post Ablation_AH']}, HV ${vals['Post Ablation_HV']}", "**ParaHisian pacing**", "${vals['Post Ablation_Parahisian']}"
    "**Incr RV pace**", "${vals['Post Ablation_Incr V Pace']}",     "**Prog RV pace**", "${vals['Post Ablation_Prog V Pace']}"
    "**Incr A pace**", "${vals['Post Ablation_Incr A Pace']}", "**Prog A pace**", "${vals['Post Ablation_Prog A Pace']}"


.. csv-table:: Conclusions
   :widths: 1, 50

     ${list2onecolcsv([vals['Conclusions_Conclusion 1'],
                    vals['Conclusions_Conclusion 2'],
		    vals['Conclusions_Conclusion 3'],
		    vals['Conclusions_Conclusion 4']])}

     
.. csv-table:: Recommendations
   :widths: 1, 50

      ${list2onecolcsv([vals['Recommendations_Recommendation 1'],
                    vals['Recommendations_Recommendation 2'],
		    vals['Recommendations_Recommendation 3'],
		    vals['Recommendations_Recommendation 4']])}


.. raw:: pdf

       Spacer 0 40
     

     
.. |jipmer| image:: /data/Dropbox/programming/EP_report2/ep_report/jipmer_logo.png
              :height: 1in
    	      :width: 1in
	      :align: middle

.. footer::

   EP report  Pg.###Page###
	      
