import thread
from ChatFns import *
from Tkinter import Tk
from tkFileDialog import askopenfilename
from tkFileDialog import asksaveasfilename
import os
import math
import re
import sys
from time import strftime
import pyaudio,wave

#---------------------------------------------------#
#---------INITIALIZE CONNECTION VARIABLES-----------#
#---------------------------------------------------#
#Initiate socket and bind port to host PC
WindowTitle = 'Chat Host'
s = socket(AF_INET, SOCK_STREAM)
sf = socket(AF_INET, SOCK_STREAM)
sv = socket(AF_INET, SOCK_STREAM)
HOST = gethostname()
PORT = int(sys.argv[1])
PORTF = PORT + 1
PORTV = PORT + 2
conn = ''
connf = ''
connv = ''
s.bind((HOST, PORT))
sf.bind((HOST, PORTF))
sv.bind((HOST, PORTV))

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
    print("* done recording\n")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open('outputc.wav', 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    LoadConnectionInfo(ChatLog, 'Voice Recording Stopped and Sending')
    conn.send('\VOICE')
    fv = open('outputc.wav', 'rb')
    for block in iter(lambda: fv.read(FILE_BUF_SIZE), ''):
        print('')
        connv.sendall(block)
    fv.close()
    LoadConnectionInfo(ChatLog, 'Voice Recording has been sent')
    os.remove('outputc.wav')
    
    
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
        conn.sendall(EntryText)
    
def FileClickActionSend():
    conn.send('\FILE')
    filename = askopenfilename()
    #ext = filename.split()[-1]
    #ext = ext[ext.find('.'):]
    ext = os.path.splitext(filename)[1]
    connf.sendall(ext)
    f = open(filename, 'rb')
    for block in iter(lambda: f.read(FILE_BUF_SIZE), ''):
        print('')
        connf.sendall(block)
    f.close()
    LoadConnectionInfo(ChatLog, 'File has been sent')
    
    
def FileClickActionRecieve():
    filename2 = connf.recv(4)
    f2 = open(str(strftime("%Y-%m-%d_%H-%M-%S"))+filename2, 'wb')
    #os.fsync(f2)
    blockdata = connf.recv(FILE_BUF_SIZE)
    while blockdata != '':
        print('')
        f2.write(str(blockdata))
        os.fsync(f2)
        if len(blockdata) < FILE_BUF_SIZE:
           break
        blockdata = ''
        blockdata = connf.recv(FILE_BUF_SIZE)
    os.fsync(f2)
    f2.close()
    LoadConnectionInfo(ChatLog, 'File has been recevived')
    

def VoiceClickAction():
    global vflag
    vflag = (vflag + 1)%2
    if(vflag == 1):
        thread.start_new_thread(audio_recording,())


def VoiceClickActionRecieve():
    fv2 = open('outputh.wav', 'wb')
    blockdatav = connv.recv(FILE_BUF_SIZE)
    while blockdatav != '':
        print('')
        fv2.write(str(blockdatav))
        os.fsync(fv2)
        if len(blockdatav) < FILE_BUF_SIZE:
           break
        blockdatav = ''
        blockdatav = connv.recv(FILE_BUF_SIZE)
    os.fsync(fv2)
    fv2.close()
    LoadConnectionInfo(ChatLog, 'Voice Recording has been recevived')
    playsound('outputh.wav')

	
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
ChatLog.insert(END, "Waiting for your partner to connect..\n")
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
def GetConnected():
    s.listen(1)
    global conn,connf,connv
    conn, addr = s.accept()
    sf.listen(1)
    connf, addrf = sf.accept()
    sv.listen(1)
    connv, addrv = sv.accept()
    LoadConnectionInfo(ChatLog, 'Connected with: ' + str(addr) + ':' + str(PORT) + '\n---------------------------------------------------------------')
    
    while 1:
        try:
            data = conn.recv(1024)
            if data == '\FILE':
                thread.start_new_thread(FileClickActionRecieve,())
                continue
            elif data == '\VOICE':
                thread.start_new_thread(VoiceClickActionRecieve,())
                continue
            LoadOtherEntry(ChatLog, data)
            if base.focus_get() == None:
                FlashMyWindow(WindowTitle)
                playsound('notif.wav')
        except:
            LoadConnectionInfo(ChatLog, '\n [ Your partner has disconnected ]\n [ Waiting for him to connect..] \n  ')
            GetConnected()

    conn.close()
    connf.close()
    connv.close()
    
thread.start_new_thread(GetConnected,())

base.mainloop()


