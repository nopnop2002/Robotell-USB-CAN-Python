import sys
import time
import serial
import struct
import logging
import Colorer
import argparse
from socket import socket, AF_INET, SOCK_DGRAM
import threading
import json

# Timer Thread
class TimerThread(threading.Thread):
    def __init__(self, ACTIVE, INTERVAL):
        threading.Thread.__init__(self)
        self.timerFlag = False
        self.interval = INTERVAL
        self.active = ACTIVE

    def run(self):
        while True:
            #print("Timer={} active={}".format(time.time(), self.active))
            if self.active == True: self.timerFlag = True
            time.sleep(self.interval)

# UDP Receive Thread
class ServerThread(threading.Thread):
    def __init__(self, PORT):
        threading.Thread.__init__(self)
        # line information
        self.HOST = ""
        self.PORT = PORT
        self.BUFSIZE = 1024
        self.ADDR = ("", self.PORT)

        # bind
        self.udpServSock = socket(AF_INET, SOCK_DGRAM)
        self.udpServSock.bind(self.ADDR)      
        self.interrupt = False

    def run(self):
        while True:
            try:
                #packet, self.addr = self.udpServSock.recvfrom(self.BUFSIZE) # Receive Data
                packet, addr = self.udpServSock.recvfrom(self.BUFSIZE) # Receive Data
                logging.debug("addr={}".format(addr))
                logging.debug("recvfrom packet={}".format(packet))
                self.packet = packet.decode()                
                json_dict = json.loads(self.packet) # If parsing fails, go to exception
                logging.debug("json_dict={}".format(json_dict))
                self.addrFrom = addr[0]
                self.portFrom = addr[1]
                logging.debug("self.addrFrom={} self.portFrom={}".format(self.addrFrom, self.portFrom))
                self.request = json_dict["request"].lower()
                if (self.request == "transmit"):
                    self.id = json_dict["id"]
                    self.type = json_dict["type"].lower()
                    logging.debug("self.request={} self.id={} self.type={}".format(self.request, self.id, self.type))
                    if (self.type == "stddata"):
                        self.data = json_dict["data"]
                        logging.debug("self.data={} len={}".format(self.data, len(self.data)), self.type)
                        self.interrupt = True
                    if (self.type == "extdata"):
                        self.data = json_dict["data"]
                        logging.debug("self.data={} len={}".format(self.data, len(self.data)))
                        self.interrupt = True
                    if (self.type == "stdremote"): self.interrupt = True
                    if (self.type == "extremote"): self.interrupt = True
                if (self.request == "filter"):
                    self.index = json_dict["index"]
                    self.id = json_dict["id"]
                    self.mask = json_dict["mask"]
                    self.type = json_dict["type"]
                    self.status = json_dict["status"]
                    logging.info("request={} index={} id={} mask={} type={} status{}".format(self.request, self.index, self.id, self.mask, self.type, self.status))
                    self.interrupt = True
            except:
                logging.error("json parse fail {}".format(self.packet))
                pass


class ParseClass(object):
    def __init__(self):
        #print("__init__")
        self.buffer = []
        self.status = 0

    def parseData(self, ch):
        logging.debug("ch=0x{:02x} {} status={} len={}".format(ch, ch, self.status, len(self.buffer)))
        if (self.status == 0):
            #print("self.status == 0")
            if (ch == 0xAA):
                self.status = 1
                self.buffer = []
                self.crc = 0
                self.buffer.append(ch)
                #print("self.buffer={}".format(self.buffer))
            return []

        elif (self.status == 1):
            #print("self.status == 1")
            if (ch == 0xAA):
                self.status = 2
                self.buffer.append(ch)
                #print("self.buffer={}".format(self.buffer))
            else:
                self.buffer = []
                self.status = 0
            return []

        elif (self.status == 2):
            #print("self.status == 2")
            #print("self.buffer={}".format(self.buffer))
            if (len(self.buffer) == 18):
                if (ch == 0xA5): # FrameCtrl,Next character is true CRC.
                    self.status = 3
                else:
                    self.crc = self.crc & 0xff
                    #print("self.crc={:x} ch={:x}".format(self.crc,ch))
                    if (self.crc != ch):
                        logging.warning("Invalid CRC(status=2) {:02x} {:02x} {}".format(self.crc, ch, self.buffer))
                        self.status = 0
                    else:
                        self.status = 8
                        self.buffer.append(ch)
            else:
                if (ch == 0xA5): # FrameCtrl,Skip this character
                    self.status = 4
                else:
                    self.crc = self.crc + ch
                    self.buffer.append(ch)
            return []

        elif (self.status == 3):
            #print("self.status == 3")
            self.crc = self.crc & 0xff
            #print("self.crc={:x} ch={:x}".format(self.crc,ch))
            if (self.crc != ch):
                logging.warning("Invalid CRC(status=3) {:02x} {:02x} {}".format(self.crc, ch, self.buffer))
                self.status = 0
            else:
                self.status = 8
                self.buffer.append(ch)
            return []

        elif (self.status == 4):
            #print("self.status == 4")
            self.crc = self.crc + ch
            self.buffer.append(ch)
            self.status = 2
            return []

        elif (self.status == 8):
            #print("self.status == 8")
            if (ch == 0x55):
                self.buffer.append(ch)
                self.status = 9
            else:
                logging.warning("invalid Packet (status=4)")
                self.status = 0
            return []

        elif (self.status == 9):
            #print("self.status == 9")
            if (ch == 0x55):
                self.buffer.append(ch)
                self.status = 9
                if (len(self.buffer) == 21):
                    logging.debug("self.buffer={}".format(self.buffer))
                    self.status = 0
                    return self.buffer
                else:
                    logging.warning("invalid Packet (status=9)")
                    self.status = 0
            else:
                logging.warning("invalid Packet (status=3)")
                self.status = 0
            return []
           
# This is old version
def _setTransmitMsg(id, rtr, ext, len, buf):
    sendData = [0xAA, 0xAA, 0x78, 0x56, 0x34, 0x12, 0x11, 0x22, 0x33, 0x44, 0x00, 0x00, 0x00, 0x00, 0x04, 0x00, 0x00, 0x00, 0x3F, 0x55, 0x55, 0xF0]
    idStr = "{:08x}".format(id)
    logging.debug("idStr={}".format(idStr))
    if (ext == 0):
        sendData[2] = int(idStr[6:8],16)
        sendData[3] = int(idStr[4:6],16) & 0x7
        sendData[4] = 0
        sendData[5] = 0
        logging.debug("id={:02x}{:02x}".format(sendData[2], sendData[3]))
    else:
        sendData[2] = int(idStr[6:8],16)
        sendData[3] = int(idStr[4:6],16)
        sendData[4] = int(idStr[2:4],16)
        sendData[5] = int(idStr[0:2],16) & 0x1F
        logging.debug("id={:02x}{:02x}".format(sendData[2], sendData[3]))
    for x in range(len):
        sendData[x+6] = buf[x]
    sendData[14] = len # Frame Data Length
    sendData[16] = ext # Standard/Extended frame
    sendData[17] = rtr # Data/Request frame
    sendData[18] = sum(sendData[2:18]) & 0xff
    print("old:crc={:2x}".format(sendData[18]))
    print("old:sendData={}".format(sendData))
    return sendData

USART_FRAMECTRL = 0xA5                                                  
USART_FRAMEHEAD = 0xAA
USART_FRAMETAIL = 0x55

def insertCtrl(buffer, ch):
    result = buffer
    #print("insertCtrl ch={:02x}".format(ch))
    if (ch == USART_FRAMECTRL or ch == USART_FRAMEHEAD or ch == USART_FRAMETAIL):
        result.append(USART_FRAMECTRL)
    return result
       
def setFilterMsg(filterIndex, filterId, filterMask, frameType, filterStatus):
    #sendData = [0xAA, 0xAA, 0xEx, 0xFE, 0xFF, 0x01, 0x11, 0x22, 0x33, 0x44, 0x00, 0x00, 0x00, 0x00, 0x04, 0x00, 0x00, 0x00, 0x3F, 0x55, 0x55, 0xF0]
    #print("sendData={}".format(sendData))

    if (filterIndex > 15):
        logging.waring("filterIndex {} is too large.".format(filterIndex))
        return []

    if (frameType.lower() != "std" and frameType.lower() != "ext"):
        logging.waring("frameType {} is invalid.".format(frameType))
        return []

    if (filterStatus.lower() != "enable" and filterStatus.lower() != "disable"):
        logging.waring("filterStatus {} is invalid.".format(filterStatus))
        return []

    sendData = [0xAA, 0xAA]
    id = 0xE0 + filterIndex
    sendData.append(id)
    crc = id
    id = 0xFE
    crc = crc + id
    sendData.append(id)
    id = 0xFF
    crc = crc + id
    sendData.append(id)
    id = 0x01
    crc = crc + id
    sendData.append(id)

    idStr = "{:08x}".format(filterId)
    if (frameType.lower() == "std"):
        id = int(idStr[6:8],16)
        sendData = insertCtrl(sendData, id)
        sendData.append(id)
        crc = crc + id
        id = int(idStr[4:6],16) & 0x7
        sendData = insertCtrl(sendData, id)
        sendData.append(id)
        crc = crc + id
        sendData.append(0)
        id = 0 # Disable
        if (filterStatus.lower() == "enable"): id = 0x80 # Enable
        sendData.append(id)
        crc = crc + id
        logging.debug("id={:02x}{:02x}".format(sendData[2], sendData[3]))
    else:
        id = int(idStr[6:8],16)
        sendData = insertCtrl(sendData, id)
        sendData.append(id)
        crc = crc + id
        id = int(idStr[4:6],16)
        sendData = insertCtrl(sendData, id)
        sendData.append(id)
        crc = crc + id
        id = int(idStr[2:4],16)
        sendData = insertCtrl(sendData, id)
        sendData.append(id)
        crc = crc + id
        id = int(idStr[0:2],16) & 0x1F
        if (filterStatus.lower() == "enable"): id = 0x80 # Enable
        sendData = insertCtrl(sendData, id)
        sendData.append(id)
        crc = crc + id
        logging.debug("id={:02x}{:02x}".format(sendData[2], sendData[3]))

    filterMaskStr = "{:08x}".format(filterMask)
    mask = int(filterMaskStr[6:8],16)
    sendData = insertCtrl(sendData, mask)
    sendData.append(mask)
    crc = crc + mask
    mask = int(filterMaskStr[4:6],16)
    sendData = insertCtrl(sendData, mask)
    sendData.append(mask)
    crc = crc + mask
    mask = int(filterMaskStr[2:4],16)
    sendData = insertCtrl(sendData, mask)
    sendData.append(mask)
    crc = crc + mask
    mask = int(filterMaskStr[0:2],16) & 0x1F
    if (frameType.lower() == "ext"):
        mask = mask + 0x40 # Extended
    sendData = insertCtrl(sendData, mask)
    sendData.append(mask)
    crc = crc + mask

    len = 8
    sendData.append(len) # Frame Data Length
    crc = crc + len
    req = 0xFF
    sendData.append(req)
    crc = crc + req
    ext = 1
    sendData.append(ext) # Standard/Extended frame
    crc = crc + ext
    rtr = 0 # Set
    sendData.append(rtr) # Set/Read
    crc = crc + rtr
    crc = crc & 0xff
    logging.debug("crc={:2x}".format(crc))
    sendData = insertCtrl(sendData, crc)
    sendData.append(crc)
    sendData.append(0x55)
    sendData.append(0x55)
    logging.debug("sendData={}".format(sendData))
    return sendData

def setTransmitMsg(id, rtr, ext, len, buf):
    #sendData = [0xAA, 0xAA, 0x78, 0x56, 0x34, 0x12, 0x11, 0x22, 0x33, 0x44, 0x00, 0x00, 0x00, 0x00, 0x04, 0x00, 0x00, 0x00, 0x3F, 0x55, 0x55, 0xF0]
    #print("sendData={}".format(sendData))

    sendData = [0xAA, 0xAA]
    idStr = "{:08x}".format(id)
    logging.debug("idStr={}".format(idStr))
    crc = 0
    if (ext == 0):
        id = int(idStr[6:8],16)
        sendData = insertCtrl(sendData, id)
        sendData.append(id)
        crc = crc + id
        id = int(idStr[4:6],16) & 0x7
        sendData = insertCtrl(sendData, id)
        sendData.append(id)
        crc = crc + id
        sendData.append(0)
        sendData.append(0)
        logging.debug("id={:02x}{:02x}".format(sendData[2], sendData[3]))
    else:
        id = int(idStr[6:8],16)
        sendData = insertCtrl(sendData, id)
        sendData.append(id)
        crc = crc + id
        id = int(idStr[4:6],16)
        sendData = insertCtrl(sendData, id)
        sendData.append(id)
        crc = crc + id
        id = int(idStr[2:4],16)
        sendData = insertCtrl(sendData, id)
        sendData.append(id)
        crc = crc + id
        id = int(idStr[0:2],16) & 0x1F
        sendData = insertCtrl(sendData, id)
        sendData.append(id)
        crc = crc + id
        logging.debug("id={:02x}{:02x}".format(sendData[2], sendData[3]))
    for x in range(len):
        sendData = insertCtrl(sendData, buf[x])
        sendData.append(buf[x])
        crc = crc + buf[x]
    if (len < 8):
        for x in range(8-len):
            sendData.append(0)
    sendData.append(len) # Frame Data Length
    crc = crc + len
    sendData.append(0)
    sendData.append(ext) # Standard/Extended frame
    crc = crc + ext
    sendData.append(rtr) # Data/Request frame
    crc = crc + rtr
    crc = crc & 0xff
    logging.debug("crc={:2x}".format(crc))
    sendData = insertCtrl(sendData, crc)
    sendData.append(crc)
    sendData.append(0x55)
    sendData.append(0x55)
    #sendData.append(0xF0)
    logging.debug("sendData={}".format(sendData))
    return sendData

# https://qiita.com/mml/items/ccc66ecc46d8299b3346
def sendMsg( buf ):
      while True:
            if ser.out_waiting == 0:
                  break
      for b in buf:
            a = struct.pack( "B", b )
            ser.write(a)
      ser.flush()
         
def initId():
    data = [0xAA, 0xAA, 0xFF, 0xFE, 0xFF, 0x01, 0x00, 0x00, 0x00, 0x80, 0x00, 0x00, 0x00, 0x00, 0x08, 0xFF, 0x01, 0x00, 0x66, 0x55, 0x55]

    data[18]=sum(data[2:18]) & 0xFF
    #print("data[18]={:02x}".format(data[18]))
    sendMsg(data)


def readInfo(id):
    data = [0xAA, 0xAA, 0xE0, 0xFF, 0xFF, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xFF, 0x01, 0x01, 0x66, 0x55, 0x55]
    idStr = "{:08x}".format(id)
    #print("idStr={}".format(idStr))
    data[2] = int(idStr[6:8],16)
    data[3] = int(idStr[4:6],16)
    data[4] = int(idStr[2:4],16)
    data[5] = int(idStr[0:2],16)
    data[18]=sum(data[2:18]) & 0xFF
    #print("data={:02x}{:02x}{:02x}{:02x}".format(data[2], data[3], data[4], data[5]))
    sendMsg(data)
     

def readFilter(index):
     data = [0xAA, 0xAA, 0xE0, 0xFE, 0xFF, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xFF, 0x01, 0x01, 0x66, 0x55, 0x55]

     #print("index={}".format(index))
     data[2] = 0xE0 + index
     data[18]=sum(data[2:18]) & 0xFF
     #print("data4[18]={:2x}".format(data4[18]))
     sendMsg(data)

def setSpeed(speed):
     logging.info("speed={}".format(speed))
     speed1000 = [0xAA, 0xAA, 0xD0, 0xFE, 0xFF, 0x01, 0x40, 0x42, 0x0F, 0x00, 0x01, 0x02, 0x00, 0x00, 0x04, 0xFF, 0x01, 0x00, 0x66, 0x55, 0x55]

     speed800 = [0xAA, 0xAA, 0xD0, 0xFE, 0xFF, 0x01, 0x00, 0x35, 0x0C, 0x00, 0x01, 0x02, 0x00, 0x00, 0x04, 0xFF, 0x01, 0x00, 0x16, 0x55, 0x55]

     speed500 = [0xAA, 0xAA, 0xD0, 0xFE, 0xFF, 0x01, 0x20, 0xA1, 0x07, 0x00, 0x01, 0x02, 0x00, 0x00, 0x04, 0xFF, 0x01, 0x00, 0x9D, 0x55, 0x55]

     speed400 = [0xAA, 0xAA, 0xD0, 0xFE, 0xFF, 0x01, 0x80, 0x1A, 0x06, 0x00, 0x01, 0x02, 0x00, 0x00, 0x04, 0xFF, 0x01, 0x00, 0x75, 0x55, 0x55]

     speed250 = [0xAA, 0xAA, 0xD0, 0xFE, 0xFF, 0x01, 0x90, 0xD0, 0x03, 0x00, 0x01, 0x02, 0x00, 0x00, 0x04, 0xFF, 0x01, 0x00, 0x38, 0x55, 0x55]

     speed125 = [0xAA, 0xAA, 0xD0, 0xFE, 0xFF, 0x01, 0x48, 0xE8, 0x01, 0x00, 0x01, 0x02, 0x00, 0x00, 0x04, 0xFF, 0x01, 0x00, 0x06, 0x55, 0x55]

     speed100 = [0xAA, 0xAA, 0xD0, 0xFE, 0xFF, 0x01, 0xA0, 0x86, 0x01, 0x00, 0x01, 0x02, 0x00, 0x00, 0x04, 0xFF, 0x01, 0x00, 0xFC, 0x55, 0x55]


     if (speed == 1000000):
         sendMsg(speed1000)
         return True
     elif (speed == 800000):
         sendMsg(speed800)
         return True
     elif (speed == 500000):
         sendMsg(speed500)
         return True
     elif (speed == 400000):
         sendMsg(speed400)
         return True
     elif (speed == 250000):
         sendMsg(speed250)
         return True
     elif (speed == 125000):
         sendMsg(speed125)
         return True
     elif (speed == 100000):
         sendMsg(speed100)
         return True
     else:
         return False

    
def loggingFrame(header, buffer):
     message = header
     message = message + "["
     for x in range(len(buffer)):
        message = message + "{:02x}".format(buffer[x]).upper()
        if (x != len(buffer)-1): message = message + " "
     message = message + "]"
     logging.info(message)

def printFrame(buffer):
     logging.debug("buffer={}".format(buffer))
     if (buffer[16] == 0): # Standard frame
         receiveId = (buffer[3] << 8) + buffer[2]
     else: # Extended frame
         receiveId = (buffer[5] << 24) + (buffer[4] << 16) + (buffer[3] << 8) + buffer[2]
     logging.debug("receiveId=0x{:X}".format(receiveId))
     if (buffer[15] == 0xFF):
         if (receiveId == 0x01fffed0):
             message = "BAUDRATE ID: 0x"
         elif (receiveId == 0x01fffff0):
             message = "CPUINFO0 ID: 0x"
         elif (receiveId == 0x01fffff1):
             message = "CPUINFO1 ID: 0x"
         elif (receiveId == 0x01ffffe0):
             message = "VERSION  ID: 0x"
         elif (receiveId == 0x01fffeff):
             message = "INIT     ID: 0x"
         elif (receiveId == 0x01fffeb0):
             message = "ABOM     ID: 0x"
         elif (receiveId == 0x01fffea0):
             message = "ART      ID: 0x"
         elif ((receiveId & 0x01fffff0) == 0x01fffee0):
             index = receiveId & 0xf
             message = "FILTER{:02d} ID: 0x".format(index)
         message = message + "{:02x}".format(buffer[5]).upper()
         message = message + "{:02x}".format(buffer[4]).upper()
         message = message + "{:02x}".format(buffer[3]).upper()
         message = message + "{:02x}".format(buffer[2]).upper()
         message = message + "  DLC: "
         message = message + "{:01n}".format(buffer[14])
         message = message + "  Data:"
         for x in range(buffer[14]):
             #print ("x={}".format(x))
             message = message + " 0x"
             message = message + "{:02x}".format(buffer[x+6]).upper()
     else:
         if (buffer[16] == 0):
             message = "Standard ID: 0x"
             message = message + "{:01x}".format(buffer[3]).upper()
             message = message + "{:02x}".format(buffer[2]).upper()
             message = message + "       DLC: "
         else:
             message = "Extended ID: 0x"
             message = message + "{:02x}".format(buffer[5]).upper()
             message = message + "{:02x}".format(buffer[4]).upper()
             message = message + "{:02x}".format(buffer[3]).upper()
             message = message + "{:02x}".format(buffer[2]).upper()
             message = message + "  DLC: "
         message = message + "{:01n}".format(buffer[14])
         message = message + "  Data:"
         if (buffer[17] == 0):
             for x in range(buffer[14]):
                 #print ("x={}".format(x))
                 message = message + " 0x"
                 message = message + "{:02x}".format(buffer[x+6]).upper()
         else:
             message = message + " REMOTE REQUEST FRAME"
     print(message)
     return receiveId
    
      
format="%(asctime)s [%(filename)s:%(lineno)d] %(levelname)-8s %(message)s"
#logging.basicConfig(level=logging.DEBUG, format=format)
#logging.basicConfig(level=logging.WARNING, format=format)

parser = argparse.ArgumentParser()
parser.add_argument("-p", "--port", help="open port")
parser.add_argument("-s", "--speed", help="can bit rate", type=int)
parser.add_argument("-u", "--udp", help="UDP receive port", type=int)
parser.add_argument("-l", "--log", dest="logLevel", choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], help="Set the logging level")

args = parser.parse_args()
device = "/dev/ttyUSB0"
speed = 500000
udpPort = 8200

if args.port:
    print("args.port={}".format(args.port))
    device = args.port
if args.speed:
    print("args.speed={}".format(args.speed))
    speed = args.speed
if args.udp:
    print("args.udp={}".format(args.udp))
    udpPort = args.udp
if args.logLevel:
    level=getattr(logging, args.logLevel)
    print("logLevel set to {}".format(level))
    #logging.basicConfig(level=getattr(logging, args.logLevel))
    logging.basicConfig(level=getattr(logging, args.logLevel), format=format)
else:
    print("logLevel set to {}".format(logging.WARNING))
    logging.basicConfig(level=logging.WARNING, format=format)

if (speed != 1000000 and speed != 500000 and speed != 400000 and speed != 250000 and speed != 125000 and speed != 100000):
    logging.error("This speed {} is not supported.".format(speed))
    sys.exit()

'''
ser = serial.Serial(
      port = "/dev/ttyUSB0",
      baudrate = 115200,
      #parity = serial.PARITY_NONE,
      #bytesize = serial.EIGHTBITS,
      #stopbits = serial.STOPBITS_ONE,
      #timeout = None,
      #xonxoff = 0,
      #rtscts = 0,
      )
'''
ser = serial.Serial(
      port = device,
      baudrate = 115200,
      #parity = serial.PARITY_NONE,
      #bytesize = serial.EIGHTBITS,
      #stopbits = serial.STOPBITS_ONE,
      #timeout = None,
      #xonxoff = 0,
      #rtscts = 0,
      )


# Start Timer thread (Timer is not use)
timer = TimerThread(ACTIVE=True, INTERVAL=5)
timer.setDaemon(True)
timer.start()

# Start UDP Receive hread
#udp = ServerThread(PORT=8200)
udp = ServerThread(PORT=udpPort)
udp.setDaemon(True)
udp.start()


buffer = []
parse = ParseClass()
receiveId = 0x01FFFFFF

while True:
    if (receiveId == 0x01FFFFFF):
        initId()
        receiveId = 0
    elif (receiveId == 0x01FFFEFF):
        setSpeed(speed)
        receiveId = 0
    elif (receiveId == 0x01FFFED0):
        readInfo(0x01FFFFE0)
        receiveId = 0
    elif (receiveId == 0x01FFFFE0):
        readInfo(0x01FFFFF0)
        receiveId = 0
    elif (receiveId == 0x01FFFFF0):
        readInfo(0x01FFFFF1)
        receiveId = 0
    elif (receiveId == 0x01FFFFF1):
        readInfo(0x01FFFEB0)
        receiveId = 0
    elif (receiveId == 0x01FFFEB0):
        readInfo(0x01FFFEA0)
        receiveId = 0
    elif (receiveId == 0x01FFFEA0):
        readFilter(0)
        receiveId = 0
    elif ((receiveId & 0x01FFFFF0) == 0x01FFFEE0):
        index = receiveId & 0xf
        #print("index={}".format(index))
        if (index != 15):
            readFilter(index+1)
            receiveId = 0
        else:
            receiveId = 0xFFFFFFFF
        
    if timer.timerFlag is True:
        #print("timeFlag")
        timer.timerFlag = False
        """
        sendData = [0xAA, 0xAA, 0x78, 0x56, 0x34, 0x12, 0x11, 0x22, 0x33, 0x44, 0x00, 0x00, 0x00, 0x00, 0x04, 0x00, 0x00, 0x00, 0x3F, 0x55, 0x55, 0xF0]
        sendData[16] =1 # Standard frame
        sendData[17] =0 # Data frame
        sendData[18] = sum(sendData[2:18]) & 0xff
        print("sendData[18]={:2x}".format(sendData[18]))
        frameId = 0xF23
        frameRequest = 0
        frameType = 1
        frameLength = 4
        frameData = [0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88]
        sendData = setTransmitMsg(frameId, frameRequest, frameType, frameLength, frameData)
        sendMsg(sendData)
        """

    if udp.interrupt is True:
        logging.info("udp interrupt request={}".format(udp.request))
        if (udp.request == "transmit"):
            logging.debug("id={} type={}".format(udp.id, udp.type))
            frameId = int(udp.id, 16)
            logging.debug("frameId={:x}".format(frameId))
            if (udp.type == "stddata"):
                frameRequest = 0
                frameType = 0
                frameLength = len(udp.data)
            if (udp.type == "extdata"):
                frameRequest = 0
                frameType = 1
                frameLength = len(udp.data)
            if (udp.type == "stdremote"):
                frameRequest = 1
                frameType = 0
                frameLength = 0
            if (udp.type == "extremote"):
                frameRequest = 1
                frameType = 1
                frameLength = 0
            frameData = []
            for x in range(frameLength):
                logging.debug("udp.data={}".format(udp.data[x]))
                frameData.append(udp.data[x])
            logging.debug("frameData={}".format(frameData))
            sendData = setTransmitMsg(frameId, frameRequest, frameType, frameLength, frameData)
            sendMsg(sendData)
            logging.info("Transmit={}".format(sendData))
            loggingFrame("Transmit=", sendData)
            udp.interrupt = False

        if (udp.request == "filter"):
            logging.info("index={} id={} mask={} type={} status={}".format(udp.index, udp.id, udp.mask, udp.type, udp.status))
            filterIndex = int(udp.index)
            filterId = int(udp.id,16)
            filterMask = int(udp.mask,16)
            frameType = udp.type
            filterStatus = udp.status
            logging.debug("filterIndex={} filterId=0x{:x} filterMask=0x{:x} frameType={} filterStatus={}".format(filterIndex, filterId, filterMask, frameType, filterStatus))
            sendData = setFilterMsg(filterIndex, filterId, filterMask, frameType, filterStatus)
            if (len(sendData) > 0):
                sendMsg(sendData)
                logging.info("Mask={}".format(sendData))
                loggingFrame("Mask=", sendData)
            udp.interrupt = False

    if ser.in_waiting > 0:
        recv_data = ser.read(1)
        #print(type(recv_data))
        a = struct.unpack_from("B",recv_data ,0)
        #print( a )
        #print(type(a))
        #print( a[0] )
        b = a[0]
        #print(type(b))
        #logging.debug("b={:02x}".format(b))

        buffer = parse.parseData(b)
        if (len(buffer) > 0):
            #logging.info("Receive={}".format(buffer))
            loggingFrame("Receive=", buffer)
            #print("receiveId={:x}".format(receiveId))
            if (receiveId == 0xFFFFFFFF):
                printFrame(buffer)
            else:
                receiveId = printFrame(buffer)


