#! /usr/bin/env python
"""

Easy (cached) access to the database table mapping IRIs to id numbers.

"""

import db

_id_by_iri = {}
_iri_by_id = {}

# in a long-running process, this could accumulate stuff we don't want
# any more; so every N additions, wipe it out again.  Obviously some
# kind of LRU would be nice, but probably not cost effective to track.
max_entries = 1000

def auto_flush():
    if len(_id_by_iri) > max_entries:
        _id_by_iri.clear()
        _iri_by_id.clear()
        
def from_id(db, id):
    try:
        return _iri_by_id[id]
    except:
        pass
    for result in db.select('iri', where="id=$id", vars=locals(), limit=1):
        text = result.txt
        auto_flush()
        _iri_by_id[id] = text
        _id_by_iri[text] = id
        return text
    raise RuntimeError("bad id %s" % `id`)


def to_id(db, iri):
    try:
        return _id_by_iri[iri]
    except:
        pass
    id = None
    for result in db.select('iri', where="text=$iri", vars=locals(), limit=1):
        id = result.id

    if id is None:
        id = db.insert('iri', text=iri)        

    auto_flush()
    _id_by_iri[iri] = id
    _iri_by_id[id] = iri
    return id
