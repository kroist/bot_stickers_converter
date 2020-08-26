import sys
from PIL import Image

def convert_to_png(inname, outname):
    im = Image.open(inname)


    xsize, ysize = im.size
    size = xsize if xsize > ysize else ysize
    
    im_res = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    im_res.paste(im, (int((size-xsize)/2), int((size-ysize)/2) ))
    im_res.save(outname)
    print('saved image as: ' + outname)


if __name__ == '__main__':
    convert_to_png(sys.argv[1], sys.argv[2])
