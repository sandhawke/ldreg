#! /usr/bin/env python
"""

Can run as a web server OR on the command line.

Given the iri of some RDF data source, figure out some stuff about it,
like what vocabularies it uses. 

Store that stuff in a SQL database.

Answer queries about that stuff, from the command line, or the web.


TODO:
    - delete older scans...?   how old?     any, as soon as this
      one is done?
    - add web API
    - support query of sparql stuff
    - abort if we find out about sparq or an existing scan
"""
__version__ = "0.0.1"

import sys
sys.path[0:0] = ('/home/sandro/ldreg/misc', '/home/ldreg/ldreg.net/misc', )  

import copy
import time
import re
import urllib2
from xml.sax.xmlreader import InputSource
from xml.sax.saxutils import prepare_input_source

import web

import rdflib
from rdflib import RDF
from rdflib.syntax.parsers.RDFXMLParser import RDFXMLParser

import debugtools
from debugtools import debug
#debugtools.tags.add('scan')

import splitter

headers = {
    'Accept': 'application/rdf+xml',
    # 'Accept': 'application/rdf+xml,application/xhtml+xml;q=0.5',
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

        # when we were getting mysterious text...
        #text = self.file.read()
        #f = open("out", "w")
        #f.write(text)
        #raise RuntimeError(lookAtOut)

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
        self.db = None

    def create(self, source, with_literals=False):

        self.start = time.time()

        sax_input = URLInputSource(source)
        self.sax_input = sax_input
        parser = RDFXMLParser()

        self.data_source_iri = source
        self.with_literals = with_literals

        if self.db: self.db_start()

        self.c = 0
        try:
            parser.parse(sax_input, ScanningSink(self))
        except AbortConnection:
            print "aborted scan."

        self.end = time.time()
        print "%d triples in %.3f seconds (%.1f t/s)" % (self.c, self.end-self.start, self.c/(self.end-self.start))

    def got_triple(self, s, p, o):
        
        self.c += 1
        if self.db: self.db_update_count()
        if self.c % 1000 == 0:
            print self.c,"triples so far"
        #if self.c > 5000:
        #    raise AbortConnection()
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
            (ns, local) = splitter.split(term)
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


    def db_start(self):
        debug('scan', 'database connection started')
        self.source_id = obtain_iri_id(self.db, self.data_source_iri)
        self.id = self.db.insert('scan', 
                                 source_id=self.source_id, 
                                 time_begun=self.start,
                                 triples=0,
                                 status=0)
        debug('scan', 'database record created', self.id)

    def db_update_count(self):
        now = time.time()
        extra = {}
        if hasattr(self, 'when_count_updated'):
            ago = now - self.when_count_updated
            if ago < 0.5:
                return
        else:
            extra['time_first_triple'] = now
        self.when_count_updated = now
        self.db.update('scan', where="id = "+str(self.id),
                       triples=self.c, **extra)
        
    def db_finish(self):
        now = time.time()
        self.db.update('scan', where="id = "+str(self.id),
                       triples=self.c, 
                       time_complete=now,
                       status=1)
        
        for (term, use) in (self.term_uses.keys()):
            (ns, local) = splitter.split(term)
            nsid = obtain_iri_id(self.db, ns)

            self.db.insert('term_use',
                           local=local,
                           namespace_id = nsid,
                           scan_id = self.id,
                           type = use,
                           count = self.term_uses[(term,use)]
                           )

        delete_old_scans(self.db, self.data_source_iri)


class ScanningSink (object):
    """ This implements what rdflib's RDFXMLHandler is expecting of the store
    """

    def __init__(self, scan):
        self.scan=scan

    def add(self, triple):
        (s,p,o) = triple
        self.scan.got_triple(s,p,o)

    def bind(self, prefix, namespace, override=False):
        debug("bind", prefix, namespace, override)

iri_obtain_cache = { }   # safe to cache, since table is append-only
def obtain_iri_id(db, iri):
    try:
        return iri_obtain_cache[iri]
    except KeyError:
        pass
    debug('scan', 'looking for iri in db', iri)
    results = db.select('iri', dict(text=iri), where="text=$text")
    debug('scan', 'result from first select:', results)
    for result in results:
        id = result.id
        iri_obtain_cache[iri] = id
        return id

    id = db.insert('iri', text=iri)
    iri_obtain_cache[iri] = id
    return id

def get_latest_scan(db, source, all_scan_ids=None):
    '''Return a record of the latest completed scan of this source.

    If an array all_scan_ids is provided, all the scan ids will be
    appended to it.
    '''
    source_id = obtain_iri_id(db, source)
    max_good_id = -1
    if all_scan_ids is None:
        all_scan_ids = []
    for r in db.select('scan', where='source_id=$source_id', vars=locals()):
        if r.status == 1 and r.id > max_good_id:
            max_good_id = r.id
            rr = copy.deepcopy(r)
        all_scan_ids.append(r.id)
    if max_good_id > -1:
        return rr
    else:
        raise Exception('no good scan in database')

def delete_old_scans(db, source):
    ids = []
    good = get_latest_scan(db, source, ids)
    for id in ids:
        if id == good.id:
            continue
        db.delete('scan', where='id='+str(id))
        db.delete('term_use', where='scan_id='+str(id))
        print "Deleting records of scan", id
    print "Kept scan", good.id

def db_showns(db, source):
    good = get_latest_scan(db, source)
    max_good_id = good.id
    print `good`
    for r in db.query("select distinct text, namespace_id from term_use, iri where scan_id=$max_good_id and iri.id=namespace_id order by text;", vars=locals()):
        print "%-4d %s" % (r.namespace_id, r.text)

def db_show(db, source, ns):
    good = get_latest_scan(db, source)
    scan_id = good.id
    ns_id = obtain_iri_id(db, ns)
    print `good`
    for r in db.select('term_use', 
                       where='scan_id=$scan_id and namespace_id=$ns_id', 
                       vars=locals()):
        print r.count, r.local
        

if len(sys.argv) > 1:

    if sys.argv[1] == 'clean':
        db = web.database(dbn='mysql', db='ldreg', user='sandro', pw='')
        db.printing = False   # override web.py config setting
        source = sys.argv[2]
        delete_old_scans(db, source)

    if sys.argv[1] == 'scan':
        a = Scan()
        a.create(sys.argv[2])
        a.show()

    if sys.argv[1] == 'scantodb':
        a = Scan()
        a.db = web.database(dbn='mysql', db='ldreg', user='sandro', pw='')
        a.db.printing = False   # override web.py config setting
        a.create(sys.argv[2])
        a.db_finish()

    if sys.argv[1] == 'showns':
        db = web.database(dbn='mysql', db='ldreg', user='sandro', pw='')
        db.printing = False   # override web.py config setting
        iri = sys.argv[2]
        db_showns(db, iri)

    if sys.argv[1] == 'show':
        db = web.database(dbn='mysql', db='ldreg', user='sandro', pw='')
        db.printing = False   # override web.py config setting
        iri = sys.argv[2]
        ns = sys.argv[3]
        db_show(db, iri, ns)

    if sys.argv[1] == 'scanlit':
        a = Scan()
        a.create(sys.argv[2], with_literals=True)
        a.show()


else:
    print 'Usage: @@@'
