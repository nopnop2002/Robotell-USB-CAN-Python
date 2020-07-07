import sys
import serial
import struct
import logging
import Colorer
import argparse

class ParseClass(object):
    def __init__(self):
        #print("__init__")
        self.buffer = []
        self.status = 0

    def parseData(self, ch):
        #print("ch={:02x} {} status={} len={}".format(ch, ch, self.status, len(self.buffer)))
        if (self.status == 0):
            #print("self.status == 0")
            if (ch == 0xAA):
                self.status = 1
                self.buffer = []
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
            self.buffer.append(ch)
            #print("self.buffer={}".format(self.buffer))
            if (len(self.buffer) == 20):
                if (ch == 0x55):
                    self.status = 3
                else:
                    logging.warning("invalid Packet (status=2)")
                    self.status = 0
            return []

        elif (self.status == 3):
            #print("self.status == 3")
            self.buffer.append(ch)
            if (len(self.buffer) == 21):
                if (ch == 0x55):
                    logging.info("self.buffer={}".format(self.buffer))
                    crc = sum(self.buffer[2:18]) & 0xff
                    logging.debug("crc={}".format(crc))
                    #crc = crc & 0xff
                    #logging.debug("crc={}".format(crc))
                    if (crc == self.buffer[18]):
                        logging.debug("CRC ok")
                        self.status = 0
                        return self.buffer
                    else:
                        logging.warning("Invalid CRC {:02x} {:02x}".format(crc, self.buffer[18]))
                        self.status = 0
                else:
                        logging.warning("invalid Packet (status=3)")
                        self.status = 0
            return []
           
# https://qiita.com/mml/items/ccc66ecc46d8299b3346
def send( buf ):
      while True:
            if ser.out_waiting == 0:
                  break
      for b in buf:
            a = struct.pack( "B", b )
            ser.write(a)
      ser.flush()
         
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
         send(speed1000)
         return True
     elif (speed == 800000):
         send(speed800)
         return True
     elif (speed == 500000):
         send(speed500)
         return True
     elif (speed == 400000):
         send(speed400)
         return True
     elif (speed == 250000):
         send(speed250)
         return True
     elif (speed == 125000):
         send(speed125)
         return True
     elif (speed == 100000):
         send(speed100)
         return True
     else:
         return False

    

def printData(buffer):
     logging.info("buffer={}".format(buffer))
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
    
      
format="%(asctime)s [%(filename)s:%(lineno)d] %(levelname)-8s %(message)s"
#logging.basicConfig(level=logging.DEBUG, format=format)
#logging.basicConfig(level=logging.WARNING, format=format)

parser = argparse.ArgumentParser()
parser.add_argument("-p", "--port", help="open port")
parser.add_argument("-s", "--speed", help="can bit rate", type=int)
parser.add_argument("-l", "--log", dest="logLevel", choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], help="Set the logging level")

args = parser.parse_args()
device = "/dev/ttyUSB0"
speed = 500000
if args.port:
    print("args.port={}".format(args.port))
    device = args.port
if args.speed:
    print("args.speed={}".format(args.speed))
    speed = args.speed
if args.logLevel:
    level=getattr(logging, args.logLevel)
    print("logLevel set to {}".format(level))
    #logging.basicConfig(level=getattr(logging, args.logLevel))
    logging.basicConfig(level=getattr(logging, args.logLevel), format=format)
else:
    print("logLevel set to {}".format(logging.WARNING))
    logging.basicConfig(level=logging.WARNING, format=format)


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


if (setSpeed(speed) == False):
    logging.error("This speed {} is not supported.".format(speed))
    sys.exit()

buffer = []
parse = ParseClass()

while True:
    if ser.in_waiting > 0:
        recv_data = ser.read(1)
        #print(type(recv_data))
        a = struct.unpack_from("B",recv_data ,0)
        #print( a )
        #print(type(a))
        #print( a[0] )
        b = a[0]
        #print(type(b))
        logging.debug("b={:02x}".format(b))

        buffer = parse.parseData(b)
        if (len(buffer) > 0):
            logging.info("buffer={}".format(buffer))
            printData(buffer)


