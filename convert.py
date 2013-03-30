#!/usr/bin/python

from PIL import Image
import svgwrite
from svgwrite.path import Path
import random

shapes = [
    'Circle',
    'Crosshatch',
    'CrosshatchRandom',
    'Zigzag',
    'Squiggle',
]

class Block(object):
    def __init__(self, image, x_offset, y_offset, block_size=8, alpha=1.0, filter_ratio=0.1):
        self.image = image
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.block_size = block_size
        self.alpha = max(alpha, 0.001)
        self.filter_ratio = filter_ratio
        
        self.intensity = self.getIntensity()

    def getIntensity(self):
        width, height = self.image.size
        pixels = []
        
        # Fill pixels list with pixel values for block
        for y in range(self.y_offset, self.y_offset + self.block_size):
            for x in range(self.x_offset, self.x_offset + self.block_size):
                if x < width and y < height:
                    pixels.append(self.image.getpixel((x,y)))
        
        # Determine average value of pixels in block
        if pixels:
            intensity = (255.0 - (sum(pixels) / len(pixels))) / (255.0 * self.alpha)
        else:
            intensity = 0
        
        # If alpha value causes the radius to exceed halfblock size, radius should be set to halfblock size
        return intensity
    
    # Stub to be overridden by subclasses
    def draw(self, svg_file):
        pass

    @property
    def left(self):
        return self.x_offset
    
    @property
    def top(self):
        return self.y_offset
    
    @property
    def right(self):
        return self.x_offset + self.block_size
    
    @property
    def bottom(self):
        return self.y_offset + self.block_size
    
    @property
    def mid_x(self):
        return self.x_offset + (self.block_size / 2)
    
    @property
    def mid_y(self):
        return self.y_offset + (self.block_size / 2)
    
class Circle(Block):
    def draw(self, svg_file):
        
        if self.intensity < self.filter_ratio:
            return
        
        rad = self.block_size/2.0
        radius = min(rad * self.intensity, rad)
        svg_file.add(svg_file.circle((self.x_offset + (self.block_size / 2), self.y_offset + (self.block_size/2)), radius))

class Crosshatch(Block):
    
    def draw(self, svg_file, max_lines=12):
        
        if self.intensity < self.filter_ratio:
            return
        
        path = Path(("M", self.left, self.top), stroke="black", stroke_width="0.3", fill="none")
        count = int((max_lines * self.intensity))
        
        left_third = self.left + (self.block_size / 4.0)
        right_third = self.left + (3 * (self.block_size / 4.0))
        top_third = self.top + (self.block_size / 4.0)
        bottom_third = self.top + (3 * (self.block_size / 4.0))
        
        for m in range(count):
            if m == 0:
                path.push("L", self.right, self.bottom)
                path.push("M", self.right, self.top)
            elif m == 1:
                path.push("L", self.left, self.bottom)
                path.push("M", self.mid_x, self.top)
            elif m == 2:
                path.push("L", self.mid_x, self.bottom)
                path.push("M", self.left, self.mid_y)
            elif m == 3:
                path.push("L", self.right, self.mid_y)
                path.push("M", left_third, self.top)
            elif m == 4:
                path.push("L", left_third, self.bottom)
                path.push("M", right_third, self.top)
            elif m == 5:
                path.push("L", right_third, self.bottom)
                path.push("M", self.left, top_third)
            elif m == 6:
                path.push("L", self.right, top_third)
                path.push("M", self.left, bottom_third)
            elif m == 7:
                path.push("L", self.right, bottom_third)
                path.push("M", left_third, self.top)
            elif m == 8:
                path.push("L", self.right, bottom_third)
                path.push("M", right_third, self.top)
            elif m == 9:
                path.push("L", self.left, bottom_third)
                path.push("M", left_third, self.bottom)
            elif m == 10:
                path.push("L", self.right, top_third)
                path.push("M", right_third, self.bottom)
            elif m == 11:
                path.push("L", self.left, top_third)
        
        
        svg_file.add(path)

class CrosshatchRandom(Block):
    
    def draw(self, svg_file, max_lines=12):
        
        if self.intensity < self.filter_ratio:
            return
        
        count = int((max_lines * self.intensity) + 0.5)
        path = None
        for _ in range(count):
            start_side = random.choice((self.left, self.top))
            
            offset = random.random() * self.block_size
            if start_side == self.left:
                x1 = self.left
                x2 = self.right
                y1 = self.top + offset
                y2 = self.bottom - offset
            else:
                x1 = self.left + offset
                x2 = self.right - offset
                y1 = self.top
                y2 = self.bottom
            
            if path is None:
                path = Path(("M", x1, y1), stroke="black", stroke_width="0.3", fill="none")
            else:
                path.push("M", x1, y1)
            path.push("L", x2, y2)
            
        svg_file.add(path)

class Zigzag(Block):
    
    def draw(self, svg_file):
        
        if self.intensity < self.filter_ratio:
            return
        
        lines = int(max(min(30 * self.intensity, 40), 1))
        y_disp = float(self.block_size) / lines
        
        start = (self.left, self.top)
        end = (self.left, self.top)
        
        path = Path(("M", self.left, self.top), stroke="black", stroke_width="0.3", fill="none")
        
        # Stop when we hit the bottom
        while start[1] < self.bottom:
            # Determine which edge we are on
            # Left
            if start[0] == self.left:
                end = (self.right, start[1] + y_disp)
            # right
            elif start[0] == self.right:
                end = (self.left, start[1] + y_disp)
            
            if end[1] < self.bottom:
                # Recalc line to terminate at bottom
                path.push('L', *end)
            
            start = end
        svg_file.add(path)

class Squiggle(Block):
    
    def draw(self, svg_file):
        
        if self.intensity < self.filter_ratio:
            return
        
        segments = int(max(min(30 * self.intensity, 40), 1))
        
        def rand_point():
            return random.uniform(self.left, self.right), random.uniform(self.top, self.bottom)
        
        start = rand_point()
        path = Path(("M",) + start, stroke="black", stroke_width="0.3", fill="none")
        for _ in range(segments):
            path.push("T", *rand_point())
        
        svg_file.add(path)


def convert(img_file, shape_name='Circle', block_size=8, alpha_value=1.0, filter_limit=0.1, outfile=None):
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
    
    # Set defaults
    if not outfile:
        outfile = "%s.svg" % outfile
    
    # Open and prepare raster image file
    image = Image.open(img_file)
    image = image.convert("L")
    
    # Initiate variables
    width, height = image.size
    x, y = 0, 0
    
    # Get shape from shape_name
    shape = globals().get(shape_name, None)
    if shape is None:
        raise Exception("Shape %s does not exist." % shape_name)
    
    # Open and prepare SVG output file
    svg = svgwrite.Drawing(outfile, size=('100%', '100%'), profile="full", viewBox="0 0 %d %d" % (width, height), )
    
    # Process image in blocks until all 
    while x < width and y < height:
        block = shape(image, x, y, block_size, alpha_value)
        block.draw(svg)
        # Delete block to save memory in large files
        del block
        # Move to next block
        x += block_size
        if x >= width:
            x =  0
            y += block_size
    
    # Save SVG file and return SVG file name
    svg.save()
    return outfile

