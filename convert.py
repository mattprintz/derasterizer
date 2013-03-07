#!/usr/bin/python

from PIL import Image
import svgwrite

# TODO: switch filter to ratio

def convert(img_file, block_size=8, alpha_value=1.0, filter_limit=None, outfile=None):
    '''
        Converts a raster image to a SVG image by converting blocks of pixels to an SVG circle
        with a radius based upon the average pixel values of the block.
        
        Arguments:
        img_file: path to file (str) or Python file object (file)
        block_size: size of block for processing (int)
        alpha_value: modifying the alpha_value allows for changing the level of contrast for images (float)
        filter_limit: rendered circles with a radius below the filter_limit are not drawn at all (float)
        outfile: path/name of output file for writing the SVG file (string)
    '''
    
    # Helper function
    def getBlockAvg(image, xoffset, yoffset, size, alpha_value):
        # Set parameters
        width, height = image.size
        pixels = []
        
        # Fill pixels list with pixel values for block
        for y in range(yoffset, yoffset+size):
            for x in range(xoffset, xoffset+size):
                if x < width and y < height:
                    pixels.append(image.getpixel((x,y)))
        
        # Determine average value of pixels in block
        average = int(sum(pixels) / len(pixels))
        
        # Radius value is determined to be half of the size times the block
        # Modifying the alpha_value allows for changing the level of contrast for images
        # If alpha value causes the radius to exceed halfblock size, radius should be set to halfblock size
        radius = min((size/2) * ((255-average) / (255.0*alpha_value)), size/2)
        return radius
    
    # Set defaults
    if filter_limit is None:
        filter_limit = block_size / 5
    if not outfile:
        outfile = "%s.svg" % outfile
    
    # Open and prepare raster image file
    image = Image.open(img_file)
    image = image.convert("L")
    
    # Initiate variables
    width, height = image.size
    x, y = 0, 0
    
    # Open and prepare SVG output file
    svg = svgwrite.Drawing(outfile, size=('100%', '100%'), profile="tiny", viewBox="0 0 %d %d" % (width, height), )
    
    # Process image in blocks until all 
    while x < width and y < height:
        # Process current block determing circle radius
        radius = getBlockAvg(image, x, y, block_size, alpha_value=alpha_value)
        # Draw circle to SVG if radius is greater than the filter_limit.
        if radius > filter_limit:
            svg.add(svg.circle((x+(block_size/2), y+(block_size/2)), radius))
        # Move to next block
        x += block_size
        if x >= width:
            x =  0
            y += block_size
    
    # Save SVG file and return SVG file name
    svg.save()
    return outfile

