from mod_python import apache, util
import convert as converter
from convert import shapes
from os import path, fdopen
import re
import tempfile
import shutil
import processor

def index(req):
    shape_choices = ''.join(['''<option value="%s">%s</option>''' % (shape, shape) for shape in shapes])
    return '''
        <html>
        <head>
        <title>Derasterizer: Raster image to SVG converter</title>
        </head>
        <body>
        <h1>Bitmap to SVG converter</h1>
        <p>Upload a bitmap file (.jpg, .png, .gif) to convert it to a SVG image.</p>
        <p></p>
        <form action="/handler.py/convert" method="post" enctype="multipart/form-data">
        Upload a file: <input name="file" id="file" type="file"><br/>
        Block size (8): <input name="block_size" type="number" min="2" max="256" placeholder="8"><br/>
        Alpha adjustment (0.0 - 2.0): <input name="alpha_value" placeholder="1.0"><br/>
        Filter limit (0.0 - 1.0): <input name="filter_limit" placeholder="0.1"><br/>
        Shape type: <select name="shape">%s</select><br/>
        <input type="submit">
        </form>
        </body>
        </html>
    ''' % shape_choices

def convert(req):
    
    uploaded_file = req.form["file"]
    leafname, ext = path.splitext(uploaded_file.filename)
    
    temp_fd, temp_name = tempfile.mkstemp(prefix="svg", suffix=ext, dir="/var/www/conversion")
    temp_file = fdopen(temp_fd, "w+b")
    shutil.copyfileobj(uploaded_file.file, temp_file)
    temp_file.seek(0)
    
    opt = {
        'block_size': int(req.form.get("block_size", None) or 8),
        'alpha_value':  float(req.form.get("alpha_value", None) or 1.0),
        'filter_limit': float(req.form.get("filter_limit", None) or 0.1),
        'shape': req.form.get("shape", None),
    }
    
    job = temp_name.split("/")[-1]
    count = processor.startConversion(temp_file, base_leaf=leafname, job=job, **opt)
    
    return ":: %s" % count
    util.redirect(req, "/handler.py/conversion?job=%s" % job)
    
    #leafname, ext = path.splitext(tmpfile.filename)
    #
    #newfile = converter.convert(tmpfile.file,
    #                            shape_name=shape,
    #                            block_size=block_size,
    #                            alpha_value=alpha_value,
    #                            filter_limit=filter_limit,
    #                            outfile="/var/www/images/%s.svg" % leafname)
    #
    #basename = path.basename(newfile)
    #
    #util.redirect(req, "/handler.py/display?img=%s" % basename)

def conversion(req, job=None):
    return "job: %s" % job

def display(req, img=None):
    return '''
        <html>
        <head>
        <title>Derasterizer: Preview</title>
        </head>
        <body>
        <img style="height:97%%; width:98%%" src="/images/%(img)s"><br/>
        <a href="/">Back</a>
        <a href="/images/%(img)s">Direct link (right-click to save)</a>
        <a href="/handler.py/fullsize?img=%(img)s">View full size</a>
        </body>
        </html>
    ''' % {'img': img}

def fullsize(req, img=None):
    svgfile = open("/var/www/images/%s" % img)
    results = re.search(r'viewBox="0 0 (\d+) (\d+)"', svgfile.read(500))
    if results:
        width, height = results.groups()
    return '''
        <html>
        <head>
        <title>Derasterizer: Full sized</title>
        </head>
        <body>
        <div style="height: %spx; width: %spx; background-image: url('/images/%s');"/>
        </body>
        </html>
    ''' % (height, width, img)
