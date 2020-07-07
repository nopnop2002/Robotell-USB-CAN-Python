# USB-CAN-Python
Python program for Robotell USB-CAN Adapter


# Background   
I've bought a Robotell USB-CAN Adapter from AliExpress.   

The Windows application is published [here](https://github.com/TheRaptus/USB-CAN-Adapter).   
But in my environment only speed setting and CAN-FRAME transmission worked, CAN-FRAME reception did not work.

So, I analyzed the communication message that flows through USB and created a new one in Python.

# Software Requiment   
- pyserial

# How to use   
'''
$ git clone https://github.com/nopnop2002/USB-CAN-Python
$ cd USB-CAN-Python
$ python ./usb-can.py --help
usage: usb-can.py [-h] [-p PORT] [-s SPEED]
                  [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]

optional arguments:
  -h, --help            show this help message and exit
  -p PORT, --port PORT  open port
  -s SPEED, --speed SPEED
                        can bit rate
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --log {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        Set the logging level
'''

- pot
  Communication port.   
  Default is /dev/ttyUSB0.   

- speed
  CAN bit rate.   
  Default is 500Kbps.   
  Supporting speed is 1M/800K/500K/400K/250K/125K/100K.   

- log
  Log level.   
  Default is WARNING.   


