#! /usr/bin/env python
"""

Given the iri of some (Semantic Web) data source, figure out some
stuff about it, like what vocabularies it uses.  And whether those
vocabularies are registerable, etc.

"""

import sys
import time

import rdflib
from rdflib import RDF


# when we fetched B, we ended up with redirect[B].final
redirect = {}

class Redirect (object):

    def __init__(self):
        self.original = None
        self.final = None

        self.last_tested = None

def vocabulary_address(term):
    '''
        1. Split off the #fragment
        2. Dereference, and follow 301, 302, 303 (NOT 307) redirects

    That gives us the nominal address of the vocabulary.  Data from
    that address tells us the trackers to use, etc.

    '''
    raise RuntimeError('not implemented')


class DataSource (object):

    def __init__(self):
        self.address = None
        self.properties = set()
        self.classes = set()
        self.subjects = set()
        self.iri_values = set()
        self.last_visited = None
        self.last_modified = None
        self.vocabularies = set()

    def visit(self, address):
        ...


class Vocabulary (DataSource):

    def __init__(self):
        self.trackers = []
        self.serves = set()





engine = create_engine('mysql://sandro:@localhost/ldreg', echo=True)
#engine = create_engine('sqlite:///:memory:', echo=True)

Session = sessionmaker(bind=engine)
Base = declarative_base()

session = Session()

iri_obtain_cache = { }   # safe to cache, since table is append-only
class IRI(Base):
    __tablename__ = 'iri'

    id = Column(Integer, primary_key=True)
    text = Column(Text)

    def __init__(self, text):
        self.text = text
        
    def __repr__(self):
        return "IRI(id=%d text=%s)" % (self.id, `self.text`)

    @staticmethod
    def obtain(text):
        '''Lookup (and create if necesssary) the IRI object with this text

        We *could* do this in __new__ I suppose, but that seems too risky.
        '''

        try:
            return iri_obtain_cache[text]
        except KeyError:
            pass
        self = session.query(IRI).filter(IRI.text==text).first()
        if self is None:
            session.add(IRI(text))
            self = session.query(IRI).filter(IRI.text==text).first()
            if self is None:
                raise RuntimeError

        iri_obtain_cache[text] = self
        return self



def iri_id(text):
    return IRI.obtain(text).id
    return row.id

# I bet sqlalchemy would do this for me, if I knew how to use relations.
def iri_text(id):
    row = session.query(IRI.text).filter(IRI.id==id).first()
    if row is None:
        raise RuntimeError
        
    return row.text
    
class Entry(Base):
    __tablename__ = 'entry'

    local = Column(String(255), primary_key=True)
    namespace_id = Column(Integer, ForeignKey('iri.id'), primary_key=True)
    source_id = Column(Integer, ForeignKey('iri.id'), primary_key=True)
    report_id = Column(Integer, ForeignKey('iri.id'), primary_key=True)
    type = Column(String(1), primary_key=True)
    when = Column(Integer)  # the time of the summary-report

    namespace = relation(IRI, 
                         primaryjoin=(namespace_id == IRI.id),
                         backref=backref('entries_as_namespace',
                                         order_by=source_id))

    def __init__(self, local, namespace_id, source_id, report_id, type, when):
        self.local = local
        self.namespace_id = namespace_id
        self.source_id = source_id
        self.report_id = report_id
        self.type = type
        self.when = when
        
    def __repr__(self):
        s = ""
        s += self.local
        s += ", ns: " + str(self.namespace_id)
        s += " (" + `self.namespace` +")"
        return s
        #return "<User('%s', %d %d %d)>" % (self.local, self.namespace_id, self.source_id, self.report_id)

    #  User.__table__
    #  metadata.Base.metadata



metadata = Base.metadata
metadata.create_all(engine) 


#   session.add_all(....)

#   parse a report...?

def add_some_users():
    session = Session()
    session.add_all([
            User('ed', 'Ed Jones', 'edspassword'),
            User('wendy', 'Wendy Williams', 'foobar'),
            User('mary', 'Mary Contrary', 'xxg527'),
            User('fred', 'Fred Flinstone', 'blah')])
    session.commit()

def show_all_users():
    session = Session()
    for i in session.query(User).order_by(User.id):
        print i.id, i

def split(iri):
    '''Split the string into (ns, local), if we can get a decent qname
    out of local.  If not, then just make local be ''.
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
    
    if local[0].isalpha() and local.isalnum():
        return (ns, local)
    else:
        return (iri, '')


def timestamp():
    # surely there's a better way to the get the fractional seconds...?
    return time.strftime('%Y-%02m-%02dT%02H:%02M:%02S.') + ("%08.8f" % (time.time() %1))[2:]

def summarize(source):

    #   for now, we scan and put it directly into the DB
    #   ... there should be an intermediate RDF format for
    #       the summary.

    entries = []
    now = int(time.time())
    graph = rdflib.ConjunctiveGraph()
    graph.load(source)
    source_id = iri_id(source)

    # should be a public place this summary data can be found.
    me = iri_id('file:/tmp/hack/%s' % timestamp())

    for (s, p, o) in graph:
        (ns, local) = split(p)
        entries.append(Entry(local, iri_id(ns), source_id, me, 'p', now))
        
        if p == RDF.type:
            (ns, local) = split(o)
            entries.append(Entry(local, iri_id(ns), source_id, me, 'c', now))

        (ns, local) = split(o)
        entries.append(Entry(local, iri_id(ns), source_id, me, 'o', now))

        (ns, local) = split(s)
        entries.append(Entry(local, iri_id(ns), source_id, me, 's', now))

    session.add_all(entries)
    # delete previous data with this same report...
    # delete very old data about this source, since we have new data
    session.commit()

def stats():
    # I dunno how to talk to do with sqlalchemy....
    import MySQLdb
    db = MySQLdb.connect(passwd="", db="ldreg")
    c=db.cursor()
    
    c.execute("""select count(distinct source_id) from entry""")
    print "Number of sources:", c.fetchone()[0]
    c.execute("""select distinct text from entry, iri where entry.source_id=iri.id""")
    for row in c.fetchall():
        print "   ", row[0]
    

    c.execute("""select count(distinct namespace_id) from entry""")
    print "Number of namespaces:", c.fetchone()[0]
    c.execute("""select distinct text from entry, iri where entry.namespace_id=iri.id""")
    for row in c.fetchall():
        print "   ", row[0]


    c.execute("""select count(distinct namespace_id, local) from entry where type='p'""")
    print "Number of properties:", c.fetchone()[0]

    c.execute("""select distinct text, local from entry, iri where entry.namespace_id=iri.id and type='p'""")
    for row in c.fetchall():
        print "   ", row

    c.execute("""select count(distinct namespace_id, local) from entry where type='c'""")
    print "Number of classes:", c.fetchone()[0]

    c.execute("""select distinct text, local from entry, iri where entry.namespace_id=iri.id and type='c'""")
    for row in c.fetchall():
        print "   ", row

    print




def find(iri):
    (ns, local) = split(iri)
    for row in session.query(Entry).filter(Entry.namespace==IRI.obtain(ns)).filter(Entry.local==local):
        print `row`
    
    print ns, "used as namespace:"
    print IRI.obtain(ns).entries_as_namespace

def xfind(iri):
    (ns, local) = split(iri)
    ns_id = iri_id(ns)

    import MySQLdb
    db = MySQLdb.connect(passwd="", db="ldreg")
    c=db.cursor()
    
    c.execute("""select distinct text, type from entry, iri where source_id=id and namespace_id="""+str(ns_id)+""" and local=%s""", (local,))
    for row in c.fetchall():
        print "   ", row
      
if len(sys.argv) > 1:

    if sys.argv[1] == 'stats':
        stats()

    if sys.argv[1] == 'add-source':
        summarize(sys.argv[2])

    if sys.argv[1] == 'find':
        find(sys.argv[2])

    if sys.argv[1] == 'a':
        add_some_users()

    if sys.argv[1] == 's':
        show_all_users()

else:
    print 'Usage: @@@'

#  for u in session.query(User).order_by(User.id)[1:3]: 

#  for name, in session.query(User.name).filter_by(fullname='Ed Jones'): 

#  for name, in session.query(User.name).filter(User.fullname=='Ed Jones'): 

#   for user in session.query(User).filter(User.name=='ed').filter(User.fullname=='Ed Jones'):

# all(), one(), and first() 

# session.query(User).filter("id<:value and name=:name").\
#...     params(value=224, name='fred').order_by(User.id).one()

#     addresses = relation("Address", order_by="Address.id", backref="user")
