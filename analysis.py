#! /usr/bin/env python
"""

Given the iri of some (Semantic Web) data source, figure out some
stuff about it, like what vocabularies it uses.  And whether those
vocabularies are registerable, etc.

"""

import sys
import time
import re

import rdflib
from rdflib import RDF


# pretty aggressive; it's for keyword for searching
word_pattern = re.compile(r'''[a-zA-Z0-9]+''')   

class Analysis (object):

    def __init__(self):
        self.data_source_iri = None
        self.endpoints = []
        self.same_as = []
        self.term_uses = set()   #   of (uri, 'p')   etc.
        self.data_values = set() 
        self.keywords = set()
        self.last_modified = None
        self.expires = None
        self.with_literals = False

    def create(self, source, with_literals=False):

        # TODO: switch to using streaming from the parser; no need to store
        # all this data
        start = time.time()

        graph = rdflib.ConjunctiveGraph()
        graph.load(source)
        self.data_source_iri = source
        self.with_literals = with_literals

        c = 0
        for (s, p, o) in graph:
            c += 1
            if isinstance(s, rdflib.URIRef):
                self.term_uses.add( (str(s), 's') )
            self.term_uses.add( (str(p), 'p') )
            if p == RDF.type:
                self.term_uses.add( (str(o), 'c') )
            if isinstance(o, rdflib.URIRef):
                self.term_uses.add( (str(o), 'o') )

            if with_literals:
                if isinstance(o, rdflib.Literal):
                    self.data_values.add( o )
                    # only do this for some datatypes...?
                    for word in re.findall(word_pattern, unicode(o)):
                        self.keywords.add(word.lower())

        end = time.time()
        print "%d triples in %.3f seconds (%.1f t/s)" % (c, end-start, c/(end-start))

    def show(self):
        print
        print "Analysis of", self.data_source_iri

        print 
        print "Terms:"
        c = 0
        for (term, use) in (self.term_uses):
            c += 1
            print "   %d. "%c, " ("+use+")",  term
            if c > 20:
                print "   ..."
                break

        if not self.with_literals:
            print "No literals scanned for this analysis."
            return

        print 
        print "Literals:"
        c = 0
        for value in (self.data_values):
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
        for word in (self.keywords):
            c += 1
            print "   %d. "%c, word
            if c > 20:
                print "   ..."
                break

    def load(self, where_from):
        raise RuntimeError('not implemented')

    def serialize(self, out):
        raise RuntimeError('not implemented')

    def from_RDF(self, graph):
        raise RuntimeError('not implemented')

    def to_RDF(self, graph):
        raise RuntimeError('not implemented')

    def add_to_database(self, session):
        raise RuntimeError('not implemented')
        
      
if len(sys.argv) > 1:

    if sys.argv[1] == 'analyze':
        a = Analysis()
        a.create(sys.argv[2])
        a.show()

    if sys.argv[1] == 'analyzel':
        a = Analysis()
        a.create(sys.argv[2], with_literals=True)
        a.show()


else:
    print 'Usage: @@@'
