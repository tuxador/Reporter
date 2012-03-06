<%
    def get(item):
        """get from dict. Else return empty string."""
	try:
	    return vals[item]
	except KeyError:
	    return ''
%>



.. csv-table:: Demographics

          "**Name**", "${vals['Demographics_Name']}", "**Age**", "${vals['Demographics_Age']}", "**Sex**", "${get('Demographics_Sex')}", "**Not there**", "${get('Not there')}"

