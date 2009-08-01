

=== Model and Terminology ===

This section conveys certain simplifying assumptions and restrictions
on RDF and Semantic Web architecture.

A '''term''' is an IRI (called a ''URI-Reference'' in the RDF specs)
which is used in some RDF graph as a subject, predicate, or object.
IRIs which occur only inside RDF literals in the graph are not
considered to be terms in the graph.

The '' '''namespace''' of a term'' is the unicode substring of the
term which start at the beginning and goes through the last "#" (hash)
or "/" (slash) character (whichever is later).  Terms which contain
neither a hash nor a slash charter, such as "mailto:sandro@hawke.org"
do not have a namespace.  (This usage of the word "namespace" is
different from XML namespaces, but it is often compatible.)

A '''vocabulary''' is a set of terms.  The ''vocabulary of a term'' is
the set of all terms which share the same namespace as the term.

A '''vocabulary graph''', also called a ''schema'' or ''ontology'', is
the RDF graph obtained by dereferencing the common namespace of the
vocabulary, following redirects if necessary.  For "slash" namespaces,
this is not necessarily the same as the graph obtained by
dereferencing each of the terms in the namespace.  For very large
vocabularies (with perhaps millions or billions of terms), the
vocabulary graph can still contain essential vocabulary metadata, even
if it does not contain data about each term.

The '''vocabulary owner''' is the person or organization who
legitimately controls the content of the the vocabulary graph.  We use
the singular ("owner") instead of "owners", assuming that if multiple
people share control, they can be considered as a single organization.

A '''data source''' is an RDF graph available via the web, possibly by
way of a SPARQL endpoint.  The data source may have either an
'identity' IRI, or an 'endpoint' IRI, or both.   If:
     
* identity, no endpoint: obtain the graph data by doing a GET on the identity IRI
* endpoint, no identity: obtain the graph data by querying that SPARQL endpoint, using the background graph
* identity and endpoint: obtain the graph data by querying that SPARQL endpoint, using the identity IRI as the graph name

ISSUE: It would be nice if there were a standard protocol for discovering the endpoint IRI from the identity IRI, perhaps using some syntactic markers inside the identity IRI, or doing a fetch of the first few triples in the graph.

