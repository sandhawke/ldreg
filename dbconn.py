#! /usr/bin/env python
"""



"""

import logging

# for now, we'll use web.py's db underlayer
import web

# **NOT** thread aware.  That's okay, we don't use threads.  But under
# tornado we'll want to be re-entrant, so we can't just always use one
# db connection.   Be carefull the db connection doesn't end up shared!
db_free_pool = []
class Connection (object):
    
    def __init__(self):
        try:
            self.db = db_free_pool.pop()
        except:
            self.db = None
        if self.db is None:
            self.db = web.database(dbn='mysql', db='ldreg', user='sandro', pw='')
            # odd that web.py defaults to printing the SQL, but it does...
            self.db.printing = True
    
    def __del__(self):
        db_free_pool.append(self.db)

    def select(self, *args, **kwargs):
        return self.db.select(*args, **kwargs)

    def insert(self, *args, **kwargs):
        return self.db.insert(*args, **kwargs)

    def update(self, *args, **kwargs):
        return self.db.update(*args, **kwargs)

    def query(self, *args, **kwargs):
        return self.db.query(*args, **kwargs)

    def delete(self, *args, **kwargs):
        return self.db.delete(*args, **kwargs)



def main():
    pass

if __name__ == "__main__": 
    main()

