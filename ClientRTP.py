import struct
from tkinter import *
import tkinter.messagebox
from PIL import Image, ImageTk
import socket
import threading, sys, traceback, os
import sys
import time
import pickle
import select


class Client:
    def __init__(self, master, sId, pUDP, sTCP):
        self.last_seq_nm = 0
        self.master = master
        self.createWidgets()
        self.frameNo = 1
        self.socketUDP = self.createUDPSocket(pUDP)
        self.socketTCP = sTCP
        self.sessionId = sId
        self.imageFile = 'temp.jpeg'
        self.start_time = 0

    def createUDPSocket(self, portUDP):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.bind(("0.0.0.0", portUDP))
            s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 32000)

        except socket.error as e:
            print(f"Error binding socket: {e}")
            sys.exit(2)
        return s

    def createWidgets(self):
        """Build GUI."""
        # Create Play button
        self.start = Button(self.master, width=20, padx=3, pady=3)
        self.start["text"] = "Play"
        self.start["command"] = self.playMovie
        self.start.grid(row=1, column=1, padx=2, pady=2)

        # Create End button
        self.start = Button(self.master, width=20, padx=3, pady=3)
        self.start["text"] = "End"
        self.start["command"] = self.closeWindow
        self.start.grid(row=1, column=2, padx=2, pady=2)
        # Create a label to display the movie
        self.label = Label(self.master, height=19)
        self.label.grid(row=0, column=0, columnspan=4, sticky=W + E + N + S, padx=5, pady=5)

    def playMovie(self):
        threading.Thread(target=self.playJPEGs).start()
        self.socketTCP.send("Go".encode())
        self.socketTCP.close()

    def checkRTPHeaderData(self, sequence_number, timestamp, ssrc, version, padding, extension, cc, marker, payload_type, timeRecv):
        if(version != 2 or padding != 0 or extension != 0 or cc != 0 or marker != 1 or payload_type != 26
        or sequence_number != self.frameNo or timeRecv - timestamp > 60 or ssrc != sessionId):
            print("Incorrect values in one of the RTC header fields:")
            print(f"Version: {version} Expected: 2")
            print(f"Padding: {padding} Expected: 0")
            print(f"Extension: {extension} Expected: 0")
            print(f"CC: {cc} Expected: 0")
            print(f"Marker: {marker} Expected: 1")
            print(f"Payload type: {payload_type} Expected: 26")
            print(f"Seq no: {sequence_number} Expected: {self.frameNo}")
            print(f"Timestamp: {timeRecv - timestamp} Expected: {timeRecv - timestamp} <= 0.06")
            print(f"SSRC: {ssrc} Expected: {sessionId}")
            return False
        return True
            
    def playJPEGs(self):
        while True:
            if(self.frameNo == 1):
                self.start_time = time.time()
                print(self.start_time)
            infds, outfds, errfds = select.select([self.socketUDP], [], [], 2)
            print(f'infds={infds}')
            if infds == []:
                break
            dat, r = self.socketUDP.recvfrom(16384)
            timeRecv = int((time.time() - self.start_time)*1000)
            print(timeRecv)
            rtp_header = struct.unpack("!BBHII",dat[:12])
            first_byte = rtp_header[0]
            second_byte = rtp_header[1]
            sequence_number = rtp_header[2]
            timestamp = rtp_header[3]
            print(timestamp)
            ssrc = rtp_header[4]
            version = (first_byte >> 6) & 0x03
            padding = (first_byte >> 5) & 0x01
            extension = (first_byte >> 4) & 0x01
            cc = first_byte & 0x0F
            marker = (second_byte >> 7) & 0x01
            payload_type = second_byte & 0x7F

            if not self.checkRTPHeaderData(sequence_number, timestamp, ssrc, version, padding, extension, cc, marker, payload_type, timeRecv):
                break

            data = dat[12:]

            # TODO Students should extract the RTP header from the byte array received
            # TODO Verify if header is correct according to the requirements stated in the assignment
            # TODO Only the part of the payload corresponding to the JPEG file should be written in the file
            print(f'len={len(data)}')
            fw = open('temp.jpeg', 'wb')
            fw.write(data)
            fw.close()
            img = Image.open(self.imageFile)
            w = img.width
            l = img.height
            print(f'w={w}. l={l}')
            photo = ImageTk.PhotoImage(img)
            self.label.configure(image=photo, height=l)
            self.label.image = photo
            self.frameNo = self.frameNo + 1

    def closeWindow(self):
        print("Destroying window")
        self.master.destroy()  # Close the gui window
        os.remove(self.imageFile)


def contactServer(serverName, serverTCPControlPort, ClientUDPport, fileName):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # connect to server control port and send message with file name and clientUDPport
    # receive a sessionID; only used for checking
    try:
        s.connect((serverName, serverTCPControlPort))
    except socket.error as e:
        print(f"Error connect TCP server socket: {e}")
        s.close()
        sys.exit(3)
    msg = (ClientUDPport, fileName)
    nmsg = pickle.dumps(msg)
    s.send(nmsg)
    nrep = s.recv(128)
    rep = pickle.loads(nrep)
    print(f'SessionId = {rep[0]}')
    return rep[0], s


if __name__ == "__main__":
    # python3 Client.py ServerName ServerTCPControlPort ClientUDPport fileName
    if len(sys.argv) != 5:
        print("Usage: python3 Client.py ServerName ServerTCPControlPort ClientUDPport fileName")
        sys.exit(1)
    else:
        serverName = sys.argv[1]
        serverTCPControlPort = int(sys.argv[2])
        clientUDPport = int(sys.argv[3])
        fileName = sys.argv[4]
        # contact server, obtaining a session ID. -1 if file does not exist
        sessionId, sockTCP = contactServer(serverName, serverTCPControlPort, clientUDPport, fileName)
        if sessionId < 0:
            print("Server refused to send video!")
            sys.exit(2)
        else:
            print("Creating window to play video")
            root = Tk()
            # Create a new client
            app = Client(root, sessionId, clientUDPport, sockTCP)
            app.master.title("Player")
            root.mainloop()
