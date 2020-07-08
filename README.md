# Robotell-USB-CAN-Python
Python program for Robotell USB-CAN Adapter


# Background   
I've bought a Robotell USB-CAN Adapter from AliExpress.   
![USB-CAN Adapter](https://user-images.githubusercontent.com/6020549/86798040-52d73e80-c0ab-11ea-802c-93aa918e1067.JPG)

The Windows application is published [here](https://github.com/TheRaptus/USB-CAN-Adapter).   
But in my environment only speed setting and CAN-FRAME transmission worked, CAN-FRAME reception did not work.

So, I analyzed the communication message that flows through USB and created a new one in Python.

# Software Requiment   
- pyserial

# How to use   
```
$ git clone https://github.com/nopnop2002/Robotell-USB-CAN-Python
$ cd Robotell-USB-CAN-Python
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
```

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


# Running on Ubuntu 18.04.4
![USBCAN-python-1](https://user-images.githubusercontent.com/6020549/86798048-55399880-c0ab-11ea-844d-5823554deff7.jpg)

# Running on Windows10
![USBCAN-python-Windows](https://user-images.githubusercontent.com/6020549/86865208-88127980-c109-11ea-8328-7a283f4c1d07.jpg)
