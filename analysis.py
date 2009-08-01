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

    def create(self, source):

        # TODO: switch to using streaming from the parser; no need to store
        # all this data
        graph = rdflib.ConjunctiveGraph()
        graph.load(source)
        self.data_source_iri = source

        for (s, p, o) in graph:
            if isinstance(s, rdflib.URIRef):
                self.term_uses.add( (str(s), 's') )
            self.term_uses.add( (str(p), 'p') )
            if p == RDF.type:
                self.term_uses.add( (str(o), 'c') )
            if isinstance(o, rdflib.Literal):
                self.data_values.add( o )
                # only do this for some datatypes...?
                for word in re.findall(word_pattern, unicode(o)):
                    self.keywords.add(word.lower())
            else:
                if isinstance(o, rdflib.URIRef):
                    self.term_uses.add( (str(o), 'o') )

    def show(self):
        print
        print "Analysis of", self.data_source_iri

        print 
        print "Terms:"
        c = 0
        for (term, use) in sorted(self.term_uses):
            c += 1
            print "   %d. "%c, " ("+use+")",  term
            if c > 20:
                print "   ..."
                break

        print 
        print "Literals:"
        c = 0
        for value in sorted(self.data_values):
            c += 1
            print "   %d. "%c, value
            if c > 20:
                print "   ..."
                break

        print 
        print "Keywords:"
        c = 0
        for word in sorted(self.keywords):
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


else:
    print 'Usage: @@@'
