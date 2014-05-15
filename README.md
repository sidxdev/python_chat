python_chat
===========

Made using https://github.com/JackZProduction/python_chat code as a base for the GUI

This is a project we made in college. Different versions signify different functionalities. More details given in respective folders.

1. v1 works on LAN. A central server is setup on a single machine. This acts as a server for peer discovery for users. When users come online, they get a list of other online users from the server which can be perodicaly updated using a refresh button. Hereafter all the work is done by the user's machine. When you click on an ip in your list of online users, chat windows are opened on both machines. The user who initiated the chat acts as a pseudo-client and the other user acts as a pseudo-host (in terms of socket programming). This was done in order to construct a hybrid system in which the server was only used for peer discovery and chat etc. was done peer to peer. Functionalities in this version include voice recording, file transfer and chat. 

2. v2 is aimed at the internet. We aimed to implement a peer to peer system over the internet. This turned out to be more difficult than we thought. So instead we implemented a chat system with client-server architecture. Central server is setup, clients connect, messages routed through the central server. Still under construction; base code up, small errors to be fixed here and there. File transfer, audio streaming, video streaming and chat implemented. A application protocol has also been setup.

Project made and running on Win8 64-bit
Dependancies to run the project are as required:

1. Python 2.7 32-bit (https://www.python.org/ftp/python/2.7.6/python-2.7.6.msi)

2. pyaudio-0.2.7.py27 (http://people.csail.mit.edu/hubert/pyaudio/packages/)

3. pygame-1.9.1.win32-py2.7 (http://www.pygame.org/download.shtml)

4. pywin32-216.win32-py2.7 (http://sourceforge.net/projects/pywin32/files/pywin32/Build216/)

5. VideoCapture-0.9-5 (http://videocapture.sourceforge.net/)
