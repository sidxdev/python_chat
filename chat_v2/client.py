import thread
import os
import socket
from ChatFns import *
import time
from time import strftime
from PIL import Image as PIL_Image
from Tkinter import *
import ImageTk
import thread
from VideoCapture import Device
import pickle

socketUser = socket(AF_INET, SOCK_STREAM)
socketUserHeartbeat = socket(AF_INET, SOCK_STREAM)
hostCentral = '192.168.43.177'
portCentral = 8050
portCentralHeartbeat = portCentral + 1
#userIP = gethostbyname(gethostname())
userIP = GetExternalIP()
userIP = userIP.replace("[","").replace("]","").replace("'","")
userIP = str(userIP)
print userIP

BUFFER_SIZE = 2048
MESSAGE_SIZE = BUFFER_SIZE - 48
CONNECTION_STATUS = False

conversations = dict()
conversationWindow = dict()
onlineList = []

def ClickAction(ip):
    conversations[ip] = ''
    thread.start_new_thread(startConversation, (ip, -1, '',))
    

def resolveProtocol(window, protocol, message):
    if protocol == 0:
        onlineList = pickle.loads(message)
        print onlineList
        print 'DIsplay online list'
        onlineList.remove(userIP)
        i = 0
        for ip in onlineList:
            SendButton = Button(base, font=30, text="Connect to "+str(ip), width="12", height=5,
                        bd=0, bg="#FFBF00", activebackground="#FACC2E",
                        command=lambda:ClickAction(ip))
            i += 1
            SendButton.place(x=6, y=40+25*i, height=20, width = 388)            
    elif protocol == 1:
        LoadOtherEntry(window['ChatLog'], message)
    elif protocol == 2:
        conversationWindow[fromIP]['FILE_FLAG'] = True
        fileToWrite = open(str(strftime("%Y-%m-%d_%H-%M-%S")) + message, 'wb')
    elif protocol == 3:
        if conversationWindow[fromIP]['FILE_FLAG'] == True:
            fileToWrite.write(message)
            os.fsync(fileToWrite)
    elif protocol == 4:
        conversationWindow[fromIP]['FILE_FLAG'] = False
        fileToWrite.close()
    elif protocol == 5:
        conversationWindow[fromIP]['VIDEO_FLAG'] = True
        conversationWindow[fromIP]['VIDEO_PACKET_RECV'] = True
        conversationWindow[fromIP]['VIDEO_PACKET_WAIT'] = True

        conversationWindow[fromIP]['videoRoot'] = Tkinter.Tk()
        conversationWindow[fromIP]['videoLabel'] = Tkinter.Label(root)
        conversationWindow[fromIP]['videoLabel'].pack()
        img = None
        tkimg = [None]  
        conversationWindow[fromIP]['videoBuffer'] = message
        displayVideo(fromIP)
        thread_new_thread(startWindow,(conversationWindow[fromIP]['videoRoot'],))
    elif protocol == 6:
        if conversationWindow[fromIP]['VIDEO_FLAG']:
            conversationWindow[fromIP]['videoBuffer'] += message
    elif protocol == 7:
        if conversationWindow[fromIP]['VIDEO_FLAG']:
            conversationWindow[fromIP]['VIDEO_PACKET_RECV'] = False
            while conversationWindow[fromIP]['VIDEO_PACKET_WAIT']:
                pass
            conversationWindow[fromIP]['VIDEO_PACKET_RECV'] = True
            conversationWindow[fromIP]['videoBuffer'] = message
    elif protocol == 8:
        conversationWindow[fromIP]['VIDEO_FLAG'] = False
        conversationWindow[fromIP]['videoRoot'].destroy()
        
        
        
def displayVideo(fromIP):
    while conversationWindow[fromIP]['VIDEO_PACKET_RECV']:
        pass
    img = PIL_Image.fromstring('RGB', (640, 480), conversationWindow[fromIP]['videoBuffer'], 'raw', 'BGR', 0, -1)
    tkimg[0] = ImageTk.PhotoImage(img)
    conversationWindow[fromIP]['videoLabel'].config(image=tkimg[0])
    conversationWindow[fromIP]['videoRoot'].update_idletasks()
    conversationWindow[fromIP]['videoRoot'].after(delay, displayVideo)
    conversationWindow[fromIP]['VIDEO_PACKET_WAIT'] = False 
        
        


def createWindow(fromIP):
    conversationWindow[fromIP]['base'].mainloop()

def SendClickAction(fromIP):
    #Write message to chat window
    EntryText = FilteredMessage(conversationWindow[fromIP]['EntryBox'].get("0.0",END))
    LoadMyEntry(conversationWindow[fromIP]['ChatLog'], EntryText)

    #Scroll to the bottom of chat windows
    conversationWindow[fromIP]['ChatLog'].yview(END)

    #Erace previous message in Entry Box
    conversationWindow[fromIP]['EntryBox'].delete("0.0",END)
            
    #Send my mesage to all others
    packData(EntryText, 1, fromIP)
    

def FileClickAction(fromIP):
    filename = askopenfilename()
    ext = os.path.splitext(filename)[1]
    packData(ext, 2, fromIP)
    fileToRead = open(filename, 'rb')
    for block in iter(lambda: fileToRead.read(MESSAGE_SIZE),''):
        packData(block, 3, fromIP)
    fileToRead.close()
    packData('', 4, fromIP)
    LoadConnectionInfo(conversationWindow[fromIP]['ChatLog'], 'File has been sent')


def VideoClickAction(fromIP):
    if conversationWindow[fromIP]['VIDEO_CAPTURE_FLAG'] == False:
        conversationWindow[fromIP]['VIDEO_CAPTURE_FLAG'] = True
        thread.start_new_thread(videoCaptureStart, (fromIP,))
    else:
        conversationWindow[fromIP]['VIDEO_CAPTURE_FLAG'] = False

def videoCaptureStart(fromIP):
    cam = Device()
    buffers,width,height = cam.getBuffer()
    packData(buffers[0:MESSAGE_SIZE], 5, fromIP)
    packData(buffers[MESSAGE_SIZE:], 6, fromIP)
    while conversationWindow[fromIP]['VIDEO_CAPTURE_FLAG']:
        buffers,width,height = cam.getBuffer()
        packData(buffers[0:MESSAGE_SIZE], 7, fromIP)
        packData(buffers[MESSAGE_SIZE:], 6, fromIP)
    packData(buffers, 8, fromIP)


    
def startConversation(fromIP, initialProtocol, initialMessage):
    global conversationWindow
    conversationWindow[fromIP] = dict()
    #conversationWindow[fromIP]['VIDEO_CAPTURE_FLAG'] = False
    conversationWindow[fromIP]['base'] = Tk()
    #conversationWindow[fromIP]['base'].title(WindowTitle)
    conversationWindow[fromIP]['base'].geometry("400x520")
    #conversationWindow[fromIP]['base'].resizable(width=FALSE, height=FALSE)
    conversationWindow[fromIP]['ChatLog'] = Text(conversationWindow[fromIP]['base'], bd=0, bg="white", height="8", width="50", font="Arial",)
    conversationWindow[fromIP]['ChatLog'].insert(END, "Connecting to your partner..\n")
    #conversationWindow[fromIP]['ChatLog'].config(state=DISABLED)
    #Bind a scrollbar to the Chat window
    conversationWindow[fromIP]['scrollbar'] = Scrollbar(conversationWindow[fromIP]['base'], command=conversationWindow[fromIP]['ChatLog'].yview, cursor="heart")
    conversationWindow[fromIP]['ChatLog']['yscrollcommand'] = conversationWindow[fromIP]['scrollbar'].set
    #Create the Send Button to send message
    conversationWindow[fromIP]['SendButton'] = Button(conversationWindow[fromIP]['base'], font=30, text="Send", width="12", height=5,
                        bd=0, bg="#FFBF00", activebackground="#FACC2E",
                        command=lambda:SendClickAction(fromIP))
    #Create the File Button to send message
    conversationWindow[fromIP]['FileButton'] = Button(conversationWindow[fromIP]['base'], font=30, text="File", width="6", height=5,
                        bd=0, bg="#00BF00", activebackground="#FACC2E",
                        command=lambda:FileClickActionSend(fromIP))
    #Create the Voice Button to send message
    conversationWindow[fromIP]['VideoButton'] = Button(conversationWindow[fromIP]['base'], font=30, text="Voice", width="6", height=5,
                        bd=0, bg="#0FFFF0", activebackground="#FACC2E",
                        command=lambda:VideoClickAction(fromIP))
    #Create the box to enter message
    conversationWindow[fromIP]['EntryBox'] = Text(conversationWindow[fromIP]['base'], bd=0, bg="white",width="29", height="5", font="Arial")
    #conversationWindow[fromIP]['EntryBox'].bind("<Return>", DisableEntry)
    #conversationWindow[fromIP]['EntryBox'].bind("<KeyRelease-Return>", PressAction)
    #Place all components on the screen
    conversationWindow[fromIP]['scrollbar'].place(x=376,y=6, height=386)
    sconversationWindow[fromIP]['ChatLog'].place(x=6,y=6, height=386, width=370)
    conversationWindow[fromIP]['EntryBox'].place(x=128, y=401, height=90, width=265)
    conversationWindow[fromIP]['SendButton'].place(x=6, y=401, height=90)
    conversationWindow[fromIP]['FileButton'].place(x=6, y=491, height=20)
    conversationWindow[fromIP]['VideoButton'].place(x=61, y=491, height=20)
    print 'window created'
    if initialProtocol >= 0:
        resolveProtocol(conversationWindow[fromIP]['base'],initialProtocol, initialMessage)
    conversationWindow[fromIP]['base'].mainloop()
    #thread.start_new_thread(createWindow, (fromIP,))
    while True:
        if conversations[fromIP]  != '':
            resolveProtocol(conversationWindow[fromIP],conversations[fromIP][0], conversations[fromIP][1])
            conversations[fromIP] = ''
    

def resolveIP(fromIP, protocol, message):
    if protocol == 0 :
        return
    if fromIP not in conversations:
        conversations[fromIP] = ''
        thread.start_new_thread( startConversation, (fromIP, protocol, message,))
    else:
        conversations[fromIP] = protocol, message
        
    
        

def emitHeartbeat():
    global socketUserHeartbeat
    while True:       
        time.sleep(1)
        try:
            socketUserHeartbeat.sendall('...') # heartbeat
            #socketUserHeartbeat.recv(3)
        except:
            print('Connection to server lost. Terminating.\n')
            CONNECTION_STATUS = False
            socketUserHeartbeat.close()
            break
    
    
def recieveData():
    global socketUser
    global base
    while CONNECTION_STATUS:
        data = ''
        while data == '':
            data = socketUser.recv(BUFFER_SIZE)
        print ('Packet Dump: ' + data + '\n')
        if data:
            print('Packet Received\n')
            fromIP = str(data[0:15])
            fromIP = fromIP.replace('x','')
            toIP = str(data[15:30])
            toIP = toIP.replace('x','')
            protocol = str(data[30:48])
            protocol = protocol.replace('x','')
            protocol = int(protocol)
            #print ('garbbb')
            #print protocol
            #print ('garrrb')
            message = str(data[48:])
            message = message.rstrip('x')
            if protocol != 0:
                resolveIP(fromIP, protocol, message)
            else:
                resolveProtocol(base,0,message)
            #print(data + '\n')
            #print('From: ' + fromIP + '\nTo: ' + toIP + '\nProtocol: ' + protocol + '\nMessage: ' + message + '\n')


def pad(data, lengthToPad):
    dataLen = len(data) % lengthToPad
    if len(data) != lengthToPad:
        for i in range (dataLen, lengthToPad):
            data = data + 'x'
    #print('\ndatalen:'+str(dataLen)+' LengthToPad:'+str(lengthToPad)+'padded: '+data+'\n')
    return data
    

def packData(data,protocol,toIP):
    global socketUserHeartbeat
    global socketUser
    if not CONNECTION_STATUS:
        socketUser.close()
        socketUserHeartbeat.close()
        return False
    fromIP = str(userIP)
    if protocol == 0:
        toIP = str(userIP)
    data = pad(data, MESSAGE_SIZE)
    iterations = len(data)/MESSAGE_SIZE
    for block in range(iterations):
        print(pad(fromIP,15) + pad(toIP,15) + pad(str(protocol),18) + data[block:(block + MESSAGE_SIZE)])
        socketUser.sendall(pad(fromIP,15) + pad(toIP,15) + pad(str(protocol),18) + data[block:(block + MESSAGE_SIZE)])
    return True

def refreshAction():
    packData('',0,userIP)
    

socketUser.connect((hostCentral, portCentral))
#socketUserHeartbeat.connect((hostCentral, portCentralHeartbeat))
print('Connected to Central Server\n')
CONNECTION_STATUS = True


try:
    #thread.start_new_thread(emitHeartbeat, ())
    thread.start_new_thread(recieveData, ())
except:
    print('Problem creating threads\n')





refreshAction()

WindowTitle = 'Home'
base = Tk()
base.title(WindowTitle)
base.geometry("400x500")
base.resizable(width=FALSE, height=FALSE)



#Personal Details
PersonalDetail = Text(base, bd=0, bg="white", height="8", width="50", font="Arial",)
PersonalDetail.insert(END, "Name.." + gethostname() + '\n')

#Create the Button to refresh
RefreshButton = Button(base, font=30, text="Refresh", width="12", height=5,
                    bd=0, bg="#11BF00", activebackground="#11CC2E",
                    command=refreshAction)

#Place all components on the screen
#scrollbar.place(x=376,y=6, height=60)
# ChatLog.place(x=6,y=6, height=60, width=370)
RefreshButton.place(x=128, y=401, height=90)
PersonalDetail.place(x=6, y=6, height=40, width=388)



base.mainloop()

