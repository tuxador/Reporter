<%
    def get(item):
        """get from dict. Else return empty string."""
	try:
	    return vals[item]
	except KeyError:
	    return ''
%>

<%
    def list2onecolcsv(lst):
        """convert items in python list to a single column csv table"""
	return '\n    '.join([',"' + x + '"' for x in lst if x.strip() != ''])	
%>

<%
    def list2line(lst):
        """convert items in python list to a single line"""
	return ', '.join([x for x in lst if x.strip() != ''])	
%>




|jipmer| AICD implant discharge Summary
============================================

Department of Cardiology
------------------------

Jawaharlal Institute of Postgraduate Medical Education and Research
--------------------------------------------------------------------

.. csv-table:: Demographics

          "**Name**", "${get('Demographics_Name')}", "**Age**", "${get('Demographics_Age')}", "**Sex**", "${get('Demographics_Sex')}"
	  "**Date of Adm.**",  "${get('Demographics_Date of Admission')}", "**Proc. date**", "${get('Demographics_Date of Procedure')}", "**Contact No.**", "${get('Demographics_Contact number')}"
  "**Hosp No.**", "${get('Demographics_Hospital Number')}", "**MRD No.**", "${get('Demographics_MRD Number')}", "**AICD No.**", "${get('Demographics_ICD Number')}"

.. csv-table:: Clinical
   :widths: 3, 10

    "**Presentation**", "${get('Clinical_Presentation')}"
    "**ECG**", "${get('Clinical_ECG')}"
    "**Echo**", "${get('Clinical_Echo')}"
    "**Other Inv**", "${get('Clinical_Other investigations')}"
 
    
.. csv-table:: Investigations

   "**Hb**", "${get('Investigations_Hb')}", "**BT**", "${get('Investigations_BT')}", "**CT**", "${get('Investigations_CT')}"
   "**Urea**", "${get('Investigations_Bld Urea')}", "**Creatinine**", "${get('Investigations_Se Creat')}", "**B Sugar**", "${get('Investigations_Bld Sugar')}"
   "**HIV**", "${get('Investigations_HIV')}", "**HBsAg**", "${get('Investigations_HBsAg')}", "**HCV** ", "${get('Investigations_HCV')}"

   
.. csv-table:: Procedure details
   :widths: 3, 10

   "**Indication for procedure**", "${get('Procedure_Indication for procedure')}"
   "**Operators**", "${list2line([get('Procedure_Operator 1'), get('Procedure_Operator 2')])}"
   "**Anaesthesia**", "${get('Procedure_Anaesthesia')}"
   "**Incision**", "${get('Procedure_Incision')}"
   "**Venous Access**", "${get('Procedure_Venous Access')}"
   "**Pocket**", "${get('Procedure_Pocket')}"
   "**Lead**", "${get('Lead_Fixation')} ${get('Lead_Coils')} ${get('Lead_Model')}, Sl. no:${get('Lead_Serial no.')}"
   "**Pulse Generator**", "${get('Pulse Generator_Model')}, Sl. no:${get('Pulse Generator_Serial no.')} (${get('Pulse Generator_Source')})"
   "**Closure**", "Subcutaneous closed with ${get('Procedure_Subcutaneous closure')}. Skin closed with ${get('Procedure_Skin closure')}"



.. csv-table:: Intra-operative measurements

   "**R wave**", "${get('Intra-operative measurements_R wave')}", "**Threshold**", "${get('Intra-operative measurements_Pacing Threshold')}", "", ""
   "**RV Imp**", "${get('Intra-operative measurements_RV Impedance')}", "**HVB Imp**", "${get('Intra-operative measurements_HV Impedance')}", "**SVC Imp**", "${get('Intra-operative measurements_SVC Impedance')}"
   
.. raw:: pdf

       Spacer 0 20

.. csv-table:: Defibrillation testing

   "**VF induction**", "${get('DFT_VF induction')}"
   "**Sensing**", "${get('DFT_Sensing')}"
   "**Shock delivered**", "${get('DFT_Shock / Success')}"
   "**Charge time**", "${get('DFT_Charge time')}"


.. csv-table:: Final Settings

   "**Mode**", "${get('Settings_Mode')}", "**Lower Rate**", "${get('Settings_Lower Rate')} bpm"
   "**RV output**","${get('Settings_RV output')}", "**RV Sensing**, "${get('Settings_Sensing')} mV"
   "**VF detection**", "> ${get('Settings_VF rate')} bpm", "**VF Therapy**", "${get('Settings_VF therapy')}"
   "**VT detection**", "> ${get('Settings_VT therapy')} bpm", "**VT Therapy**", "${get('Settings_VT therapy')}"


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
		      get('Medications_Drug 6')])}
		    
.. raw:: pdf

       Spacer 0 40
     
    
| **Dr. Raja Selvaraj**
| **Assistant Professor of Cardiology**
| **JIPMER**

      
     
.. |jipmer| image:: /data/Dropbox/programming/EP_report2/icd_report/jipmer_logo.png
                  :height: 1in
                  :width: 1in
	    	  :align: middle

.. footer::

   Page ###Page### 
