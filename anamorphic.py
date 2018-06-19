import pylab as pyl
import matplotlib as mpl
import numpy as npy
import matplotlib.image as im
import time

from Tkinter import *
import Image
from PIL import Image

from numpy import log
import tkFileDialog
import tkSimpleDialog as tksd

WINDOW = 600 # window size

def idle(parent, canvas):
    print "idle"
def load_png():
    # the user chooses which .png file to open
    global pngName
    pngName = tkFileDialog.askopenfilename()
    canvas.itemconfigure("text",text="view image, and/or calculate")
    canvas.update()
    print pngName
    return pngName
def set_radius():
    # the user sets the radius
    global r_in
    r_in = tksd.askfloat("set radius", "enter the cylinder radius in inches:", maxvalue = 60, minvalue = .01, parent = root)
    canvas.itemconfigure("text",text="radius (in inches) = %.1f"%r_in)
    canvas.update()
    time.sleep(1)
    canvas.itemconfigure("text",text="please choose a .png")
    canvas.update()
    return r_in
def see_orig():
    # the user can view the image
    global pngName
    Orig = pyl.asarray(Image.open(pngName))
    Im = Image.fromarray(Orig); Im.show();
def calc_transform():
    # this transforms x -> theta, and y -> r, and gives you then new image
    try:
        global pngName, r_in, Im
        print "calculating..."
        # loading the image
        Orig = pyl.asarray(Image.open(pngName))
        Im = Image.fromarray(Orig, 'RGB');
        # checking the dpi 
        try:
            dpi = Im.info["dpi"]
            print "dpi = ", dpi
        except:
            dpi = 72
            print "couldn't find dpi, using default dpi = 72"
        print "calculating, please wait..."
        canvas.itemconfigure("text",text="Calculating, may take several mins...")
        canvas.update()
        # getting the size of the original image.  sy is the number of pixels in the y dimension, sx in the x direction, and sc is the number of colors (usually 3 for RGB or 4 if it also includes alpha)
        (sy,sx,sc) = (Orig.shape[0], Orig.shape[1], Orig.shape[2])
        # calculates the radius in pixels
        r_cylinder = int(r_in*dpi);
        # sets theta to be between 0 and pi (maybe user should be able to set this?)
        th_range = (pyl.pi)
        # sets the maximum radius (in pixels) as the radius of the cylinder plus the height of the original image.  Maybe the user should be able to set this, but then we'd have to interpolate to resize the image.
        max_r = r_cylinder+sy
        # the final image has dimensions 2*max_r x 2*max_r, because this is the widest that a circle with radius max_r will be
        fy = 2*max_r
        fx = 2*max_r
        # initialize the final image to 255s (white background)
        Final = 255*pyl.ones((fy,fx,sc), dtype = pyl.uint8)
        for y in range(fy):
            # x and y index into the final image
            # xc and yc are centered versions of x and y, so the origin is in the middle
            yc = fy/2 - y
            for x in range(fx):
                xc = fx/2 - x
                # calculate r from xc and yc
                r = pyl.sqrt(xc*xc+yc*yc)
                # calculate theta with arctan2, which works even for angles that are bigger than 90
                th = (pyl.arctan2(1.*yc,(1.*xc)))
                # check if r and theta are within range
                if ((th<th_range)&(th>0)):
                    if ((r>r_cylinder)&(r<(max_r))):
                        # x_orig and y_orig are the indices you want for the original image
                        x_orig = int(th*sx/th_range)
                        y_orig = int(r - r_cylinder)
                        # assign the appropriate pixels of the final image based on the original image, flipping up down and left right (mirror image)
                        Final[y,x,:] = Orig[sy-y_orig-1,sx - x_orig -1,:];
        # make an image out of the array, and set the dpi
        Im = Image.fromarray(Final); Im.info["dpi"] = dpi;
        canvas.itemconfigure("text",text="calculated, view and/or save the anamorphic image")
        canvas.update()
    except:
        canvas.itemconfigure("text",text="Sorry, there was an error.  Please check .png")
        canvas.update()
def see_final():
    global Im
    # show the image
    Im.show();
    return Im
def save_final():
    global Im
    canvas.itemconfigure("text",text="saving...")
    canvas.update()
    # open a dialog to save the image
    Im.save(tkFileDialog.asksaveasfilename())
    canvas.itemconfigure("text",text="saved!")
    canvas.update()

# GUI setup
root = Tk()
root.title("Emily's Anamorphics (press q to exit)")
root.bind('q','exit')
canvas = Canvas(root, width=WINDOW, height=.25*WINDOW, background='white')
# button to set radius
set_r = Button(root, text = "set radius", command = set_radius)
set_r.pack()
# button to choose .png
pickfile = Button(root, text = "choose .png", command = load_png)
pickfile.pack()
# button to view .png
see_im = Button(root, text = "view original .png", command = see_orig)
see_im.pack()
# button to run the calculations
calc = Button(root, text = "calculate anamorphic image", command=calc_transform)
calc.pack()
# button to view the results
see_fin = Button(root, text = "view anamorphic image", command = see_final)
see_fin.pack()
# button to save the results
save_fin = Button(root, text = "save anamorphic image", command =save_final)
save_fin.pack()
canvas.create_text(.5*WINDOW,.05*WINDOW,text="~Morph an image so it only looks right when viewed in a refective cylinder~",font=("Helvetica", 14),tags="explanation",fill="#0000b0")
canvas.create_text(.5*WINDOW,.1*WINDOW,text="please set the cylinder radius",font=("Helvetica", 24),tags="text",fill="#0000b0")
canvas.pack()
root.mainloop()

