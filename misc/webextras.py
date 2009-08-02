
# things for working with web.py
import os.path
import web


def serveStatic(filename):
    if ( filename.startswith("/") or
         filename.find("//") > -1 or
         filename.find("..") > -1 ):
        return notFound(filename)

    (filename, contentType) = getFileAndType(filename)
    
    web.header('Content-Type', contentType)
    web.expires(60)

    stream = open(filename, 'r')

    data = stream.read()
    stream.close()
    return data


mimeTypes = (
    ( ".css", "text/css; charset=utf-8" ),
    ( ".html", "text/html; charset=utf-8" ),
    ( ".js", "text/javascript; charset=utf-8" ),
    ( ".jpg", "image/jpeg" ),
  )
    
def getFileAndType(filename):
    filename = "static/"+filename
    for (suffix, contentType) in mimeTypes:
        if ( os.path.exists(filename) and 
             filename.lower().endswith(suffix.lower())
             ):
            return (filename, contentType)
        for usedSuffix in [suffix, suffix.lower(), suffix.upper()]:
            if ( os.path.exists(filename+usedSuffix) ):
                filename += usedSuffix
                return (filename, contentType)

    
def notFound(filename):
    web.expires(60)
    web.header('Content-Type', 'text/html')
    s =  """<p>You were looking for "%s".</p>""" % filename
    s += """<p>(on host %s)</p>""" % web.ctx.host
    s += """<p>(that is, URL="%s")</p>""" % web.url()
    s += """<p>alas.</p>"""
    web.notfound()
    return s


class static:
    def GET(self, filename):
        webextras.serveStatic(filename)
