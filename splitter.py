
def split(iri):
    '''Split the string into (ns, local), if we can get a decent qname
    out of local.  If not, then just make local be ''.

     should be doing the qname test (NCName)
     http://www.w3.org/TR/xml-names/#NT-NCName
     http://www.w3.org/TR/REC-xml/#NT-Name
     namechar: 

    NameStartChar	   ::=   	":" | [A-Z] | "_" | [a-z] | [#xC0-#xD6] | [#xD8-#xF6] | [#xF8-#x2FF] | [#x370-#x37D] | [#x37F-#x1FFF] | [#x200C-#x200D] | [#x2070-#x218F] | [#x2C00-#x2FEF] | [#x3001-#xD7FF] | [#xF900-#xFDCF] | [#xFDF0-#xFFFD] | [#x10000-#xEFFFF]
[4a]   	NameChar	   ::=   	NameStartChar | "-" | "." | [0-9] | #xB7 | [#x0300-#x036F] | [#x203F-#x2040]

    '''
    try:
        (ns, local) = iri.rsplit('#', 1)
        ns += "#"
    except ValueError:
        try:
            (ns, local) = iri.rsplit('/', 1)
            ns += "/"
        except ValueError:
            return (iri, '')

    if len(local) > 0 and local[0].isalpha(): # and local.isalnum():
        return (ns, local)
    else:
        return (iri, '')

