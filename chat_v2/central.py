import thread
from ChatFns import *
import time
import pickle

socketCentral = socket(AF_INET, SOCK_STREAM)
socketCentralHeartbeat = socket(AF_INET, SOCK_STREAM)
hostCentral = ''
portCentral = 8050
portCentralHeartbeat = 8051
socketCentral.bind((hostCentral, portCentral))
socketCentralHeartbeat.bind((hostCentral, portCentralHeartbeat))

BUFFER_SIZE = 2048 #Keep value above 48 as first 48 bytes will be header data
HEADER_SIZE = 48
MESSAGE_SIZE = BUFFER_SIZE - HEADER_SIZE
CONNECTION_ID = 1

onlineList = dict() #maintain list of online connections


def isOnline(ip):
    global onlineList
    if ip in onlineList:
        return True
    else:
        return False

    
class customException(Exception):
    pass

def pad(data, lengthToPad):
    dataLen = len(data) % lengthToPad
    if len(data) != lengthToPad:
        for i in range (dataLen, lengthToPad):
            data = data + 'x'
    return data


def sendList(ip):
    global onlineList
    try:
        print onlineList.keys()
        onlineList[ip].sendall(pad(ip,15) + pad(ip,15) + pad('0',18) + pad(str(pickle.dumps(onlineList.keys())), MESSAGE_SIZE)) #serialize array to send
        print(pad(ip,15) + pad(ip,15) + pad('0',18) + pad(str(pickle.dumps(onlineList.keys())), MESSAGE_SIZE))
        #print('Online List sent to key ' + ip + '\n')
    except:
        print('Unable to send online list to ' + ip + '\n')


def resolvePacket(data, addr):
    global onlineList
    #if not isOnline(addr):
    #    raise customException
    try:  
        fromIP = str(data[0:15])
        fromIP = fromIP.replace('x','')
        print('From IP: ' + fromIP)
        toIP = str(data[15:30])
        toIP = toIP.replace('x','')
        print('\nTo IP: ' + toIP)
        protocol = str(data[30:48])
        print('\nProtocol: ' + protocol)
        protocol = protocol.rstrip('x')
        print('\nProtocol: ' + protocol)
        protocol = int(protocol)      
    except:
        print('Unable to get packet credentials\n')
    print('From IP: ' + fromIP + '\nTo IP: ' + toIP + '\nProtocol: ' + str(protocol) + '\nMessage: ' + data[48:] + '\n')
    #print('Packet dump: ' + data + '\n')
    #print('Packet Received. From Credentials: ' + onlineList[fromIP] + ' To Credentials: ' + onlineList[toIP] + '\n')
    if protocol == 0:
        print('Sending online list to key ' + toIP + '\n')
        sendList(toIP)
    else:
        onlineList[toIP].sendall(data)
    print('Packet Sent to key' + addr + '\n')
    

def listenForHeartbeat(connHeartbeat, addr):
    global onlineList
    connHeartbeat.settimeout(1.5)
    while True:
        time.sleep(1)
        if not isOnline(addr):
            break
        try:
            connHeartbeat.recv(3) # heartbeat
            #connHeartBeat.sendall('...')
        except:
            print(addr + ' heartbeat disconnected\n')
            onlineList[addr].close()
            del onlineList[addr]
            connHeartbeat.close()
            break
    

def listenForConnection():
    socketCentral.listen(5)
    conn,addr = socketCentral.accept()
    print(str(addr) + ' connected\n')
    #socketCentralHeartbeat.listen(5)
    #connHeartbeat,addrHeartbeat = socketCentralHeartbeat.accept()
    #print connHeartbeat.gettimeout()
    #print(str(addr) + ' heartbeat connected\n')

    onlineList[str(addr[0])] = conn
    #thread.start_new_thread(listenForHeartbeat, (connHeartbeat, str(addr[0]),))
    thread.start_new_thread(listenForConnection, ())
    while True:
        if not isOnline(str(addr[0])):
            print(str(addr) + ' disconnected\n')
            break
        try:
            data = ''
            while data == '':
                data = onlineList[str(addr[0])].recv(BUFFER_SIZE)
            print('Packet received from key ' + str(addr[0]) + '\n')
            print('Packet dump: ' + data + '\n')
            #conn.sendall('')
            resolvePacket(data,str(addr[0]))
            #print('Packet sent to key ' + str(addr[0]) + '\n')
        except:
            print('Unable to send data to ' + str(addr[0]) + '. Terminating Connection.\n')
            del onlineList[str(addr[0])]
            break


print('Server started at External IP: ' + GetExternalIP() + ' Internal IP: ' + gethostbyname(gethostname()) + '\n')
thread.start_new_thread(listenForConnection, ())

while True:
    pass
