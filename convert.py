#!/usr/bin/python

from PIL import Image
import svgwrite

BOX_SIZE = 8
FILTER = 1.5
ALPHA = 1.0

def getSquareAvg(image, xoffset, yoffset, size, alpha):
    width, height = image.size
    pixels = []
    for y in range(yoffset, yoffset+size):
        for x in range(xoffset, xoffset+size):
            if x < width and y < height:
                pixels.append(image.getpixel((x,y)))
    average = int(sum(pixels) / len(pixels))
    radius = min((size/2) * ((255-average) / (255.0*alpha)), size/2)
    return radius

def convert(filename, box_size=BOX_SIZE, alpha=ALPHA, filter_size=FILTER, outfile=None):
    image = Image.open(filename)
    image = image.convert("L")
    
    width, height = image.size
    x, y = 0, 0
    
    if outfile is None:
        outfile = "%s.svg" % outfile
    
    svg = svgwrite.Drawing(outfile, profile="tiny")
    
    while x < width and y < height:
        d = getSquareAvg(image, x, y, box_size, alpha=alpha)
        if d > filter_size:
            svg.add(svg.circle((x+(box_size/2), y+(box_size/2)), d))
        x += box_size
        if x >= width:
            x =  0
            y += box_size
    svg.save()
    return outfile

