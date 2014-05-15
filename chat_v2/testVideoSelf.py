from VideoCapture import Device
from socket import *
from PIL import Image as PIL_Image
import Tkinter
import ImageTk
import thread

def captureVideo():
    global im
    while True:
        buffers,width,height = cam.getBuffer()
        im = PIL_Image.fromstring('RGB', (width, height), buffers, 'raw', 'BGR', 0, -1)
        Tkinter.Label(root, image=tkimage).pack()
        

cam = Device()
#print cam.saveSnapshot('2.jpg')
#print cam.getImage().save('3.jpg')

buffers,width,height = cam.getBuffer()

#im = PIL_Image.fromstring('RGB', (width, height), buffers, 'raw', 'BGR', 0, -1)

#print len(buffers)

#im.save('4.jpg')

print 'done'

root = Tkinter.Tk()
label = Tkinter.Label(root)
label.pack()
img = None
tkimg = [None]  # This, or something like it, is necessary because if you do not keep a reference to PhotoImage instances, they get garbage collected.

buffers,width,height = cam.getBuffer()
img = PIL_Image.fromstring('RGB', (width, height), buffers, 'raw', 'BGR', 0, -1)
print len(buffers)
delay = 10   # in milliseconds
def loopCapture():
    #print "capturing"
    buffers,width,height = cam.getBuffer()
    img = PIL_Image.fromstring('RGB', (width, height), buffers, 'raw', 'BGR', 0, -1)
    #img = Image.new('1', (100, 100), 0)
    tkimg[0] = ImageTk.PhotoImage(img)
    label.config(image=tkimg[0])
    root.update_idletasks()
    root.after(delay, loopCapture)
    #print('here')

loopCapture()
root.mainloop()
