


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

