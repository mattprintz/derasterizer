from mod_python import apache, util
import convert as converter
from os import path

def index(req):
    return '''
        <html>
        <head>
        <title>Bitmap to SVG</title>
        </head>
        <body>
        <h1>Bitmap to SVG converter</h1>
        <p>Upload a bitmap file (.jpg, .png, .gif) to convert it to a SVG image.</p>
        <p></p>
        <form action="/handler.py/convert" method="post" enctype="multipart/form-data">
        Upload a file: <input name="file" id="file" type="file"><br/>
        Block size (8): <input name="box_size" type="number" min="1" max="256" placeholder="8"><br/>
        Alpha adjust (1.0): <input name="alpha_value" type="number" min="0" max="1" placeholder="1.0"><br/>
        Filter limit (1.5): <input name="filter_limit" type="number" min="0" placeholder="1.5"><br/>
        <input type="submit">
        </form>
        </body>
        </html>
    '''

def convert(req):
    tmpfile = req.form["file"]
    block_size = int(req.form["box_size"] or 8)
    alpha_value = float(req.form["alpha_value"] or  1.0)
    filter_limit = float(req.form["filter_limit"] or (block_size / 5))
    
    leafname, ext = path.splitext(tmpfile.filename)
    
    newfile = converter.convert(tmpfile.file,
                                box_size=block_size,
                                alpha=alpha_value,
                                filter_size=filter_limit,
                                outfile="/var/www/images/%s.svg" % leafname)
    
    basename = path.basename(newfile)
    
    util.redirect(req, "/handler.py/display?img=%s" % basename)

def display(req, img=None):
    return '''
        <html>
        <head>
        <title>Bitmap to SVG</title>
        </head>
        <body>
        <img style="height:98%%; width:98%%" src="/images/%s"><br/>
        <a href="/">Back</a>
        </body>
        </html>
    ''' % img