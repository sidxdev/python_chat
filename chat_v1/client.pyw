import thread
from ChatFns import *
from Tkinter import Tk
from tkFileDialog import askopenfilename
from tkFileDialog import asksaveasfilename
import os
import math
import sys
from time import strftime
import pyaudio, wave

#---------------------------------------------------#
#---------INITIALIZE CONNECTION VARIABLES-----------#
#---------------------------------------------------#
WindowTitle = 'Chat Client'
HOSTP = str(sys.argv[1])
#HOST='192.168.1.2'
#PORTP = int(sys.argv[2])
HOST=HOSTP
PORTP = 8012
sp = socket(AF_INET, SOCK_STREAM)
s = socket(AF_INET, SOCK_STREAM)
sf = socket(AF_INET, SOCK_STREAM)
sv=socket(AF_INET,SOCK_STREAM)
FILE_BUF_SIZE = 2048

vflag = 0

def audio_recording():
    global vflag
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    
    print('')
    LoadConnectionInfo(ChatLog, 'Voice Recording Started')
    frames = []
    #for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    while True:
        if vflag == 0:
            break
        datav = stream.read(CHUNK)
        print('')
        frames.append(datav)
        

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open('outputh.wav', 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    LoadConnectionInfo(ChatLog, 'Voice Recording Being Sent')
    s.send('\VOICE')
    fv = open('outputh.wav', 'rb') 
    for block in iter(lambda: fv.read(FILE_BUF_SIZE), ''):
        print('')
        sv.sendall(block)
    fv.close()
    LoadConnectionInfo(ChatLog, 'Voice Recording Sent')
    os.remove('outputh.wav')

#---------------------------------------------------#
#------------------ MOUSE EVENTS -------------------#
#---------------------------------------------------#
def SendClickAction():
    #Write message to chat window
    EntryText = FilteredMessage(EntryBox.get("0.0",END))
    LoadMyEntry(ChatLog, EntryText)

    #Scroll to the bottom of chat windows
    ChatLog.yview(END)

    #Erace previous message in Entry Box
    EntryBox.delete("0.0",END)
            
    #Send my mesage to all others
    s.sendall(EntryText)

def FileClickActionSend():
    s.send('\FILE')
    filename = askopenfilename()
    flen=len(filename)
    ext=os.path.splitext(filename)[1]
    #ext=filename.split()[-1]
    #ext=ext[ext.find('.'):]
    sf.sendall(ext)
    f = open(filename, 'rb') 
    for block in iter(lambda: f.read(FILE_BUF_SIZE), ''):
        print('')
        sf.sendall(block)
    f.close()
    LoadConnectionInfo(ChatLog, 'File has been sent')
    
    
def FileClickActionRecieve():
    ext=sf.recv(4)
    f2 = open(str(strftime("%Y-%m-%d_%H-%M-%S"))+ext, 'wb')
    #os.fsync(f2)
    blockdata=sf.recv(FILE_BUF_SIZE)
    while blockdata !='':
        print('')
        f2.write(blockdata)
        os.fsync(f2)
        if len(blockdata) < FILE_BUF_SIZE :
            break
        blockdata=''
        blockdata=sf.recv(FILE_BUF_SIZE)
    os.fsync(f2)
    f2.close()
    LoadConnectionInfo(ChatLog, 'File has been received')
    
def VoiceClickAction():
    global vflag
    vflag = (vflag + 1)%2
    if(vflag == 1):
        thread.start_new_thread(audio_recording,())

def VoiceClickActionRecieve():
    fv2 = open('outputc.wav', 'wb')
    #os.fsync(f2)
    blockdatav=sv.recv(FILE_BUF_SIZE)
    while blockdatav !='':
        print('')
        fv2.write(blockdatav)
        os.fsync(fv2)
        if len(blockdatav) < FILE_BUF_SIZE :
            break
        blockdatav=''
        blockdatav=sv.recv(FILE_BUF_SIZE)
    os.fsync(fv2)
    fv2.close()
    LoadConnectionInfo(ChatLog, 'Voice Recording Received')
    playsound('outputc.wav')

#---------------------------------------------------#
#----------------- KEYBOARD EVENTS -----------------#
#---------------------------------------------------#
def PressAction(event):
	EntryBox.config(state=NORMAL)
	SendClickAction()
def DisableEntry(event):
	EntryBox.config(state=DISABLED)
    

#---------------------------------------------------#
#-----------------GRAPHICS MANAGEMENT---------------#
#---------------------------------------------------#

#Create a window
base = Tk()
base.title(WindowTitle)
base.geometry("400x520")
base.resizable(width=FALSE, height=FALSE)

#Create a Chat window
ChatLog = Text(base, bd=0, bg="white", height="8", width="50", font="Arial",)
ChatLog.insert(END, "Connecting to your partner..\n")
ChatLog.config(state=DISABLED)

#Bind a scrollbar to the Chat window
scrollbar = Scrollbar(base, command=ChatLog.yview, cursor="heart")
ChatLog['yscrollcommand'] = scrollbar.set

#Create the Send Button to send message
SendButton = Button(base, font=30, text="Send", width="12", height=5,
                    bd=0, bg="#FFBF00", activebackground="#FACC2E",
                    command=SendClickAction)

#Create the File Button to send message
FileButton = Button(base, font=30, text="File", width="6", height=5,
                    bd=0, bg="#00BF00", activebackground="#FACC2E",
                    command=FileClickActionSend)

#Create the Voice Button to send message
VoiceButton = Button(base, font=30, text="Voice", width="6", height=5,
                    bd=0, bg="#0FFFF0", activebackground="#FACC2E",
                    command=VoiceClickAction)

#Create the box to enter message
EntryBox = Text(base, bd=0, bg="white",width="29", height="5", font="Arial")
EntryBox.bind("<Return>", DisableEntry)
EntryBox.bind("<KeyRelease-Return>", PressAction)

#Place all components on the screen
scrollbar.place(x=376,y=6, height=386)
ChatLog.place(x=6,y=6, height=386, width=370)
EntryBox.place(x=128, y=401, height=90, width=265)
SendButton.place(x=6, y=401, height=90)
FileButton.place(x=6, y=491, height=20)
VoiceButton.place(x=61, y=491, height=20)

#---------------------------------------------------#
#----------------CONNECTION MANAGEMENT--------------#
#---------------------------------------------------#

def ReceiveData():
    try:
        sp.connect((HOSTP, PORTP))
        counter=int(sp.recv(4))
        sp.close()
        PORT = counter
        PORTF = counter+1
        PORTV = counter+2
        s.connect((HOST, PORT))
        LoadConnectionInfo(ChatLog, '[ Succesfully connected : ' + str(counter)  +']\n---------------------------------------------------------------')
        sf.connect((HOST, PORTF))
        sv.connect((HOST,PORTV))
    except:
        LoadConnectionInfo(ChatLog, '[ Unable to connect ]')
        return
    
    while 1:
        try:
            data = s.recv(1024)
            if  data == '\FILE':
                thread.start_new_thread(FileClickActionRecieve,())
                continue
            elif  data == '\VOICE':
                thread.start_new_thread(VoiceClickActionRecieve,())
                continue
        except:
            LoadConnectionInfo(ChatLog, '\n [ Your partner has disconnected ] \n')
            break
        if data != '':
            LoadOtherEntry(ChatLog, data)
            if base.focus_get() == None:
                FlashMyWindow(WindowTitle)
                playsound('notif.wav')
                
        else:
            LoadConnectionInfo(ChatLog, '\n [ Your partner has disconnected ] \n')
            break
    s.close()
    sf.close()
    sv.close()

thread.start_new_thread(ReceiveData,())

base.mainloop()


