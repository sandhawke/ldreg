

=== Model and Terminology ===

This section conveys certain simplifying assumptions and restrictions
on RDF and Semantic Web architecture.

A '''term''' is an IRI (called a ''URI-Reference'' in the RDF specs)
which is used in some RDF graph as a subject, predicate, or object.
IRIs which occur only inside RDF literals in the graph are not
considered to be terms in the graph.

A term is '''splittable''' if it ends with either a "#" (hash) or "/"
(slash) character followed by an NCName (as per XML Namespaces).  We
limit ourselves to hash and slash for simplicity; the NCName
restriction means that the IRI can potentially be abbrivated as a
QName in RDF/XML.

The '''namespace part''' (or, less formally, the '''namespace''') of a
''splittable term'' is the unicode substring up to and including the
delimiter (hash or slash).  Terms which are not splittable do not have
namespace parts.    (This usage of the word "namespace" is
different from XML namespaces, but it is generally compatible.)  

A '''vocabulary''' is a set of terms which all have the same namespace
part.  The ''vocabulary of a term'' is the set of all terms which
share the same namespace part as the term.

A '''vocabulary graph''', also called a ''schema'' or ''ontology'', is
the RDF graph obtained by dereferencing the namespace part of any/all
terms in the vocabulary, following redirects as necessary.  For
"slash" namespaces, this is not necessarily the same as the graph
obtained by dereferencing any of the terms in the namespace.  For
very large vocabularies (with perhaps millions or billions of terms),
the vocabulary graph can still contain essential vocabulary metadata,
even if it does not contain data about each term.

The '''vocabulary owner''' (or '''maintainer''') is the person or
organization who legitimately controls the content of the the
vocabulary graph.  We use the singular ("owner") instead of "owners",
assuming that if multiple people share control, they can be considered
as a single organization.

A '''data source''' is an RDF graph available via the web, possibly by
way of a SPARQL endpoint.  The data source may have either an
''identity'' IRI, or an ''endpoint'' IRI, or both.   If:
     
* identity, no endpoint: obtain the graph data by doing a GET on the identity IRI
* endpoint, no identity: obtain the graph data by querying that SPARQL endpoint, using the background graph
* identity and endpoint: obtain the graph data by querying that SPARQL endpoint, using the identity IRI as the graph name

See [[Using SPARQL]].

A '''tracker''' is a database (with a web front-end) operating on
behalf of one or more vocabularies owners, maintaining a list of the
data sources which use each term in the vocabulary.  A '''vocabulary
is tracked''' if it has one or more trackers operating on its behalf,
and those trackers are properly indicated in the vocabulary graph.  A
term is '''trackable''' if its vocabulary is tracked.

A data source is ''registered'' if, for each trackable term it uses,
the source's use of that term is recorded by all the trackers assigned
to track the vocabulary containing that term.  Where ''tracking''
involves the relationship between a data source and a vocabulary,
''registration'' is a broader concept, involving the relationship
between data source and the Semantic Web as a whole.

A '''scan''' is an RDF Graph which lists the terms used by some data
source.  A '''scanner''' is a program or service which produces scans.
Scans are used to reduce the need for trackers to read the complete
contents of data sources.



=== Provided Vocabularies ===

for use inside vocabulary graphs:

   <> ldreg:tracker <...tracker url...>

for use inside data sources, if you're providing an end-point

   <> ns1:sparqlProxy <...endpoint address...>
   [sort of interverse of saddle:dataSet]

   see http://lists.w3.org/Archives/Public/www-archive/2009Aug/0001
   (on that, note that http extensions might just be <> properties)

for use inside data sources:

   <> ldreg:analysis <...url of analysis of this source...>

for use inside an analysis

   <Analysis>
      <dataSource>
         <DataSource rdf:about="... data source ...">
            <endpoint rdf:resource="... end point address ...">
      <PropertyUse>
   eh...    don't need to be so reified.

     <> a Analysis.
     <... data source ...>
         sameAs  <...  other URLs for same data source ...>
         endpoint < ... sparql endpoint ... >
         usesProperty <... property1 ...>
         usesProperty <... property2 ...>
         usesClass <... property2 ...>
         usesSubject
	 #  eh, no, we should actually count the triples
	 #  and report the counts.   AND maybe we should be
	 #  counting the different subjects using some property
	 #      instance-count vs triple-count

         termUse [
              a PropertyUse
              term <... prop1 ...>
              triples  18
              subjects 6
         ]

         termUse [
              a SubjectUse
              term <... subject7 ...>
              triples  200
              subjects 4
	      # tell us some of the most common properties used with
	      # this subject/property/class/object ?
              relatedProperty <... p7 ...>
	      # hmmm:   (inverse of termUse.   might make better RDF/XML)
              source <... dataSourceIdent ...>
         ]
         
         usesObjectValue
	 usesTerm   (superproperty of those)

	 usesDataValue
	 usesKeyword    (alphanumeric sequence, lowercased)


          AnalysisWithoutLiterals
	  AnalysisWithLiterals

         lastModified
         expires

         dc:creator (of analysis)

================


    <> ldreg:scan <...address of a scanner report...>

the scanner report (the scan) says:

    - which namespaces are in use
         link to sub-report for each one, so trackers only
         need to download the ones for their own vocabs
         [ or inline if small?   nah, just like html+images, http
	 can handle this. ]
    - possibly link to word index
    - possibly link to sparql server
    
so, IF you provide a link to a scan report, then you can be tracked
much more easily.   if not, someone has to scan you first.


================

