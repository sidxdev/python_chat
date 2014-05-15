import thread
import os
import socket
from ChatFns import *
import time

socketUser = socket(AF_INET, SOCK_STREAM)
socketUserHeartbeat = socket(AF_INET, SOCK_STREAM)
hostCentral = '122.177.31.222'
portCentral = 8050
portCentralHeartbeat = portCentral + 1
userIP = gethostbyname(gethostname())

BUFFER_SIZE = 2048
MESSAGE_SIZE = BUFFER_SIZE - 48
CONNECTION_STATUS = False

def resolveProtocol(fromIP, protocol, message):
    pass

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
    while CONNECTION_STATUS:
        data = socketUser.recv(BUFFER_SIZE)
        if data:
            print('Packet Received\n')
            fromIP = str(data[0:15])
            fromIP.replace('x','')
            toIP = str(data[15:30])
            toIP.replace('x','')
            protocol = str(data[30:48])
            protocol.replace('x','')
            message = str(data[48:])
            message = message.rstrip('x')
            resolveProtocol(fromIP, protocol, message)
            #print(data + '\n')
            #print('From: ' + fromIP + '\nTo: ' + toIP + '\nProtocol: ' + protocol + '\nMessage: ' + message + '\n')


def pad(data, lengthToPad):
    dataLen = len(data) % lengthToPad
    for i in range (dataLen, lengthToPad):
        data = data + 'x'
    return data
    

def packData(data):
    global socketUserHeartbeat
    global socketUser
    if not CONNECTION_STATUS:
        socketUser.close()
        socketUserHeartbeat.close()
        return False
    fromIP = userIP
    toIP = userIP
    protocol = ''
    data = pad(data, MESSAGE_SIZE)
    iterations = len(data)/MESSAGE_SIZE
    for block in range(iterations):
        #print(pad(fromIP,15) + pad(toIP,15) + pad(protocol,18) + data[block:(block + MESSAGE_SIZE)])
        socketUser.sendall(pad(fromIP,15) + pad(toIP,15) + pad(protocol,18) + data[block:(block + MESSAGE_SIZE)])
    return True

socketUser.connect((hostCentral, portCentral))
socketUserHeartbeat.connect((hostCentral, portCentralHeartbeat))
print('Connected to Central Server\n')
CONNECTION_STATUS = True


try:
    thread.start_new_thread(emitHeartbeat, ())
    thread.start_new_thread(recieveData, ())
except:
    print('Problem creating threads\n')

while True:
    data = raw_input('\nYou: ')
    if(not packData(data)):
        break
