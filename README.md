# Robotell-USB-CAN-Python
Python program for Robotell USB-CAN Adapter


# Background   
I've bought a Robotell USB-CAN Adapter from AliExpress.   
![USB-CAN Adapter](https://user-images.githubusercontent.com/6020549/86798040-52d73e80-c0ab-11ea-802c-93aa918e1067.JPG)

The Windows application is published [here](https://www.amobbs.com/thread-4651667-1-1.html).   
The link described as "ourdev_627692IXWNNX.rar" in the page is the Windows application.   
But I can't understand Chinese.   

So, I analyzed the communication message that flows through USB and created a new application with Python.

# Software Requiment   
- pyserial

- socat

# How to use   
```
$ git clone https://github.com/nopnop2002/Robotell-USB-CAN-Python
$ cd Robotell-USB-CAN-Python
$ python ./usb-can.py --help
usage: usb-can.py [-h] [-p PORT] [-s SPEED] [-u UDP]
                  [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]

optional arguments:
  -h, --help            show this help message and exit
  -p PORT, --port PORT  open port
  -s SPEED, --speed SPEED
                        can bit rate
  -u UDP, --udp UDP     UDP receive port
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --log {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        Set the logging level
```

- port   
  Communication port.   
  Default is /dev/ttyUSB0.   
  __Be sure to specify the correct port in Windows 10.__   

- speed   
  CAN bit rate.   
  Default is 500Kbps.   
  Supporting speed is 1M/800K/500K/400K/250K/125K/100K.   

- udp   
  UDP port number for receive   
  Default is 8200   

- log   
  Log level.   
  Default is WARNING.   

# Information of the USB-CAN Adapter   
These displays are internal information of the USB-CAN Adapter, not CAN FRAME.   

- BAUDRATE is the current speed.   
 0x20-0xA1-0x07-0x00 is 0x0007A120(=500,000)   

- VERSION is firmware version.   

- FILTERxx is the current receive filter setting.   
 The initial value enables reception of all CAN FRAMEs.   

```
BAUDRATE ID: 0x01FFFED0  DLC: 4  Data: 0x20 0xA1 0x07 0x00
VERSION  ID: 0x01FFFFE0  DLC: 8  Data: 0x01 0x00 0x00 0x00 0xC5 0x24 0x00 0x08
CPUINFO0 ID: 0x01FFFFF0  DLC: 8  Data: 0x57 0xFF 0x73 0x06 0x67 0x75 0x54 0x55
CPUINFO1 ID: 0x01FFFFF1  DLC: 8  Data: 0x11 0x30 0x17 0x67 0x00 0x00 0x00 0x00
ABOM     ID: 0x01FFFEB0  DLC: 8  Data: 0x00 0x00 0x00 0x00 0xC5 0x24 0x00 0x08
ART      ID: 0x01FFFEA0  DLC: 8  Data: 0x00 0x00 0x00 0x00 0xC5 0x24 0x00 0x08
FILTER00 ID: 0x01FFFEE0  DLC: 8  Data: 0x00 0x00 0x00 0x80 0x00 0x00 0x00 0x00
FILTER01 ID: 0x01FFFEE1  DLC: 8  Data: 0x00 0x00 0x00 0xC0 0x00 0x00 0x00 0x00
FILTER02 ID: 0x01FFFEE2  DLC: 8  Data: 0xFF 0xFF 0xFF 0x5F 0xFF 0xFF 0xFF 0x1F
FILTER03 ID: 0x01FFFEE3  DLC: 8  Data: 0xFF 0xFF 0xFF 0x5F 0xFF 0xFF 0xFF 0x1F
FILTER04 ID: 0x01FFFEE4  DLC: 8  Data: 0xFF 0xFF 0xFF 0x5F 0xFF 0xFF 0xFF 0x1F
FILTER05 ID: 0x01FFFEE5  DLC: 8  Data: 0xFF 0xFF 0xFF 0x5F 0xFF 0xFF 0xFF 0x1F
FILTER06 ID: 0x01FFFEE6  DLC: 8  Data: 0xFF 0xFF 0xFF 0x5F 0xFF 0xFF 0xFF 0x1F
FILTER07 ID: 0x01FFFEE7  DLC: 8  Data: 0xFF 0xFF 0xFF 0x5F 0xFF 0xFF 0xFF 0x1F
FILTER08 ID: 0x01FFFEE8  DLC: 8  Data: 0xFF 0xFF 0xFF 0x5F 0xFF 0xFF 0xFF 0x1F
FILTER09 ID: 0x01FFFEE9  DLC: 8  Data: 0xFF 0xFF 0xFF 0x5F 0xFF 0xFF 0xFF 0x1F
FILTER10 ID: 0x01FFFEEA  DLC: 8  Data: 0xFF 0xFF 0xFF 0x5F 0xFF 0xFF 0xFF 0x1F
FILTER11 ID: 0x01FFFEEB  DLC: 8  Data: 0xFF 0xFF 0xFF 0x5F 0xFF 0xFF 0xFF 0x1F
FILTER12 ID: 0x01FFFEEC  DLC: 8  Data: 0xFF 0xFF 0xFF 0x5F 0xFF 0xFF 0xFF 0x1F
FILTER13 ID: 0x01FFFEED  DLC: 8  Data: 0xFF 0xFF 0xFF 0x5F 0xFF 0xFF 0xFF 0x1F
FILTER14 ID: 0x01FFFEEE  DLC: 8  Data: 0x00 0x00 0x00 0x00 0x01 0x00 0x00 0x00
FILTER15 ID: 0x01FFFEEF  DLC: 8  Data: 0xFF 0xFF 0xFF 0xBF 0xFF 0xFF 0xFF 0xFF
```

# CAN transmission data
This tool accepts data to send via UDP Broadcast.   
Open a new terminal and execute the following command:   
```
$ chmod 777 transmit.sh
$ vi transmit.sh

Please change if necessary.

$ ./transmit.sh
```

# CAN receive filter settings(Standard Frame)
This tool accepts filter to set via UDP Broadcast.   
Open a new terminal and execute the following command:   
```
$ chmod 777 stdmask.sh
$ vi stdmask.sh

Please change if necessary.

$ ./stdmask.sh
```

# CAN receive filter settings(Extended Frame)
This tool accepts filter to set via UDP Broadcast.   
Open a new terminal and execute the following command:   
```
$ chmod 777 extmask.sh
$ vi extmask.sh

Please change if necessary.

$ ./extmask.sh
```

# Running on Ubuntu 18.04.4
![USBCAN-python-1](https://user-images.githubusercontent.com/6020549/86798048-55399880-c0ab-11ea-844d-5823554deff7.jpg)

# Running on Windows10
![USBCAN-python-Windows](https://user-images.githubusercontent.com/6020549/86865771-9dd46e80-c10a-11ea-9a17-962add35e729.jpg)

# Trouble shooting
Change the log level when the program starts.   
You can see receive & transmit packet.   
![USB-CAN -python-LogLevel](https://user-images.githubusercontent.com/6020549/86876808-74bed880-c120-11ea-85d1-6502682dbbdf.jpg)
