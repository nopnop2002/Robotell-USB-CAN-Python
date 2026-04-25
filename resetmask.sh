#!/bin/bash

# index
#   index of filter(0-15)
# id
#   filter id
# mask
#   filter mask
# type
#   std : for Standard frame
#   ext : for Extended frame
# status
#   Enable  : Enable filter
#   disable : Disable filter

# Reset All filter
json=$(cat << EOS
{
  "request": "Filter",
  "index": 0,
  "id": "0x000",
  "mask": "0x000",
  "type": "std",
  "status": "Enable"
}
EOS
)

echo "$json"
echo "$json"  | socat - udp-datagram:255.255.255.255:8200,broadcast

json=$(cat << EOS
{
  "request": "Filter",
  "index": 1,
  "id": "0x000",
  "mask": "0x000",
  "type": "ext",
  "status": "Enable"
}
EOS
)

echo "$json"
echo "$json"  | socat - udp-datagram:255.255.255.255:8200,broadcast


