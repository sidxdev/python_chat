import thread
import os
import string
import socket as custom_socket
from ChatFns import *

#---------------------------------------------------#
#---------INITIALIZE CONNECTION VARIABLES-----------#
#---------------------------------------------------#
WindowTitle = 'Home'
HOSTC = "192.168.43.177"
PORTC = 8011
sc = socket(AF_INET, SOCK_STREAM)
sl = socket(AF_INET, SOCK_STREAM)
HOSTL = custom_socket.gethostbyname(custom_socket.gethostname())
PORTL = 8012
sl.bind((HOSTL,PORTL))
counter = PORTL + 1

#---------------------------------------------------#
#------------------ MOUSE EVENTS -------------------#
#---------------------------------------------------#
def ClickAction(IP):
    os.system('client.pyw '+IP)

def RefreshActionThread():
    sc.sendall("1")
    i=0
    global SendButton
    try:
        data = sc.recv(1024)
    except:
        LoadConnectionInfo(ChatLog, '\n [ Your partner has disconnected ] \n')
    if data != '':
        data = data.replace("[","").replace("]","").replace("'","").replace('"',"").replace('(','').replace(')','').split(",")
        print(data)
        for dataentry in data:
            #Create the Button to send message
            try:
                SendButton = Button(base, font=30, text="Connect to "+str(dataentry), width="12", height=5,
                        bd=0, bg="#FFBF00", activebackground="#FACC2E",
                        command=lambda:ClickAction(dataentry))
            except:
                continue
            i+=1 
            SendButton.place(x=6, y=40+25*i, height=20, width =388)
            
def RefreshAction():
    #global SendButton
    #SendButton.place(x=0,y=0,height=0,width=0)
    #SendButton.destroy()
    thread.start_new_thread(RefreshActionThread,())

#---------------------------------------------------#
#----------------- KEYBOARD EVENTS -----------------#
#---------------------------------------------------#
def PressAction(event):
	EntryBox.config(state=NORMAL)
	ClickAction()
def DisableEntry(event):
	EntryBox.config(state=DISABLED)
    

#---------------------------------------------------#
#-----------------GRAPHICS MANAGEMENT---------------#
#---------------------------------------------------#

#Create a window
base = Tk()
base.title(WindowTitle)
base.geometry("400x500")
base.resizable(width=FALSE, height=FALSE)


#Personal Details
PersonalDetail = Text(base, bd=0, bg="white", height="8", width="50", font="Arial",)
PersonalDetail.insert(END, "Name.." + gethostname() + '\n')
PersonalDetail.insert(END, 'IP: ' + str(HOSTL))
PersonalDetail.insert(END, "\nStatus..\n") #TextEditable

#Create a Chat window
#ChatLog = Text(base, bd=0, bg="white", height="8", width="50", font="Arial",)
#ChatLog.insert(END, "Connecting to your partner..\n")
#ChatLog.config(state=DISABLED)

#Bind a scrollbar to the Chat window
#scrollbar = Scrollbar(base, command=ChatLog.yview, cursor="heart")
#ChatLog['yscrollcommand'] = scrollbar.set

#Create the Button to refresh
RefreshButton = Button(base, font=30, text="Refresh", width="12", height=5,
                    bd=0, bg="#11BF00", activebackground="#11CC2E",
                    command=RefreshAction)

#Place all components on the screen
#scrollbar.place(x=376,y=6, height=60)
# ChatLog.place(x=6,y=6, height=60, width=370)
RefreshButton.place(x=128, y=401, height=90)
PersonalDetail.place(x=6, y=6, height=40, width=388)

#---------------------------------------------------#
#----------------PARSING DATA-----------------------#
#---------------------------------------------------#
        

#---------------------------------------------------#
#----------------CONNECTION MANAGEMENT--------------#
#---------------------------------------------------#

def ReceiveData():
    try:
        sc.connect((HOSTC, PORTC))
        #LoadConnectionInfo(ChatLog, '[ Succesfully connected to Central Server ]\n---------------------------------------------------------------')
    except:
        #LoadConnectionInfo(ChatLog, '[ Unable to connect ]')
        return
    
    while 1:
        try:
            data = sc.recv(1024)
        except:
            #LoadConnectionInfo(ChatLog, '\n [ Your partner has disconnected ] \n')
            break
        if data != '':
            print('')
            data = data.replace("[","").replace("]","").replace("'","").replace('"',"").replace('(','').replace(')','').split(",")
            print(data)
                    
        else:
            #LoadConnectionInfo(ChatLog, '\n [ Your partner has disconnected ] \n')
            break
    sc.close()

def open_chat(counter):
    os.system("host.pyw " + str(counter))

def listening_for_connection():
    global counter
    sl.listen(5)
    conn,addr = sl.accept()
    print('')
    conn.sendall(str(counter))
    #data = conn.recv(1024)
    #print('Chat started with ' + data)
    thread.start_new_thread(open_chat,(counter,))
    counter += 3
    #conn.close()
    thread.start_new_thread(listening_for_connection,())

thread.start_new_thread(ReceiveData,())
thread.start_new_thread(listening_for_connection,())
#thread.start_new_thread(RefreshActionThread,())



base.mainloop()
print('hi;')
