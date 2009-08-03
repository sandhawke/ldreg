#! /usr/bin/env python
"""

Given the iri of some (Semantic Web) data source, figure out some
stuff about it, like what vocabularies it uses.  And whether those
vocabularies are registerable, etc.

TODO:
    - record on-going status in DB
    - abort if we find out about sparq or an existing scan
    - segment the scan by namespace
"""
__version__ = "0.0.1"

import sys
import time
import re
import urllib2
from xml.sax.xmlreader import InputSource
from xml.sax.saxutils import prepare_input_source

import rdflib
from rdflib import RDF
from rdflib.syntax.parsers.RDFXMLParser import RDFXMLParser

import tracker

headers = {
    'Accept': 'application/rdf+xml,application/xhtml+xml;q=0.5',
    'User-agent': 'ldregscan-%s (sandro@hawke.org)' % __version__
    }

# borrowed from rdflib
class URLInputSource(InputSource, object):
    def __init__(self, system_id=None):
        super(URLInputSource, self).__init__(system_id)
        self.url = system_id
        # So that we send the headers we want to...
        req = urllib2.Request(system_id, None, headers)
        self.file = urllib2.urlopen(req)
        self.setByteStream(self.file)
        # TODO: self.setEncoding(encoding)

    def __repr__(self):
        return self.url


def incr(dict, key):
    try:
        dict[key]+=1
    except KeyError:
        dict[key]=1

# pretty aggressive; it's for keyword for searching
word_pattern = re.compile(r'''[a-zA-Z0-9]+''')   

class AbortConnection(RuntimeError):
    pass

class Scan (object):

    def __init__(self):
        self.data_source_iri = None
        self.endpoints = []
        self.same_as = []
        self.term_uses = {}   #   key is (uri, 'p'), value is counter
        self.data_values = {}  # value is counter
        self.keywords = {} #  value is counter
        self.last_modified = None
        self.expires = None
        self.with_literals = False

    def create(self, source, with_literals=False):

        start = time.time()

        sax_input = URLInputSource(source)
        self.sax_input = sax_input
        parser = RDFXMLParser()

        self.data_source_iri = source
        self.with_literals = with_literals

        self.c = 0
        try:
            parser.parse(source, ScanningSink(self))
        except AbortConnection:
            print "aborted scan."

        end = time.time()
        print "%d triples in %.3f seconds (%.1f t/s)" % (self.c, end-start, self.c/(end-start))

    def got_triple(self, s, p, o):

        self.c += 1
        if self.c % 1000 == 0:
            print self.c,"triples so far"
        if self.c > 5000:
            raise AbortConnection()
        if isinstance(s, rdflib.URIRef):
            incr(self.term_uses, (str(s), 's'))
        incr(self.term_uses,  (str(p), 'p') )
        if p == RDF.type:
            incr(self.term_uses,  (str(o), 'c') )
        if isinstance(o, rdflib.URIRef):
            incr(self.term_uses,  (str(o), 'o') )

        if self.with_literals:
            if isinstance(o, rdflib.Literal):
                incr(self.data_values, o )
                # only do this for some datatypes...?
                for word in re.findall(word_pattern, unicode(o)):
                    incr(self.keywords, word.lower())


    def show(self):
        print
        print "Scan of", self.data_source_iri

        self.show_by_ns()

        print 
        print "Terms:"
        c = 0
        for (term, use) in (self.term_uses.keys()):
            c += 1
            print "   %d. "%c, " ("+use+")",  term, "x", self.term_uses[(term,use)]
            if c > 20:
                print "   ..."
                break

        if not self.with_literals:
            print "No literals scanned for this scan."
            return

        print 
        print "Literals:"
        c = 0
        for value in (self.data_values.keys()):
            c += 1
            print "   %d. "%c, `value[1:80]`,
            if len(value) > 80:
                print "..."
            else:
                print
            if c > 20:
                print "   ..."
                break

        print 
        print "Keywords:"
        c = 0
        for word in (self.keywords.keys()):
            c += 1
            print "   %d. "%c, word
            if c > 20:
                print "   ..."
                break

    def show_by_ns(self):
        ns_count = {}
        for (term, use) in (self.term_uses.keys()):
            (ns, local) = tracker.split(term)
            if ns and local:
                incr(ns_count, ns)
        print ns_count

    def load(self, where_from):
        raise RuntimeError('not implemented')

    def serialize(self, out):
        # hmmmm.   just use to_RDF and let rdflib serialize it, or
        # do my own constrained XML, so XML tools can read it, too?
        raise RuntimeError('not implemented')

    def from_RDF(self, graph):
        raise RuntimeError('not implemented')

    def to_RDF(self, graph):
        raise RuntimeError('not implemented')

    def add_to_database(self, session):
        raise RuntimeError('not implemented')
        

class ScanningSink (object):
    """ This implements what rdflib's RDFXMLHandler is expecting of the store
    """

    def __init__(self, scan):
        self.scan=scan

    def add(self, triple):
        (s,p,o) = triple
        self.scan.got_triple(s,p,o)

    def bind(self, prefix, namespace, override=False):
        print "bind", prefix, namespace, override
      
if len(sys.argv) > 1:

    if sys.argv[1] == 'scan':
        a = Scan()
        a.create(sys.argv[2])
        a.show()

    if sys.argv[1] == 'scanlit':
        a = Scan()
        a.create(sys.argv[2], with_literals=True)
        a.show()


else:
    print 'Usage: @@@'
