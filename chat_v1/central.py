import thread
from ChatFns import *

s = socket(AF_INET, SOCK_STREAM)
HOST = gethostname()
PORT = 8011
conn = ''
s.bind((HOST, PORT))

online_list = []

def send_list(conn):
    try:
        conn.send(str(online_list))
    except:
        print('Unable to send online list to ' + str(conn) + '\n')

def listen_for_connection():
    s.listen(5)
    conn,addr = s.accept()
    print(str(addr) + ' connected \n')
    online_list.append(str(addr[0]))
    thread.start_new_thread(listen_for_connection,()) 
    while True:
        try:
            try:
                online_list.remove(str(addr[0]))
                conn.send(str(online_list))
                online_list.append(str(addr[0]))
                data = conn.recv(1)
            except:
                print('Unable to send online list to ' + str(conn) + '\n')
                print(str(addr) + ' disconnected \n')
                online_list.remove(str(addr[0]))
                break
        except:
            print(str(addr) + ' disconnected \n')
            online_list.remove(str(addr[0]))
            break   
        

thread.start_new_thread(listen_for_connection,())

while True:
    pass
