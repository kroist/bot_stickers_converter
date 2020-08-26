import sys, io
from PIL import Image

def convert_to_png(infile):
    im = Image.open(infile)



    xsize, ysize = im.size
    size = xsize if xsize > ysize else ysize

    
    im_res = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    im_res.paste(im, (int((size-xsize)/2), int((size-ysize)/2) ))

    im_res = im.resize((512, 512))

    print('all is cool')

    out = io.BytesIO()
    im_res.save(out, 'PNG')
    out.seek(0)
    return out


if __name__ == '__main__':
    with open('photo1.jpg', 'rb') as fil1:
        myfile = convert_to_png(fil1)
        with open('photo2.png', 'wb') as fil2:
            fil2.write(myfile.read())
