#!/bin/bash

# Enable 0x103 and 0x106
json=$(cat << EOS
{
  "request": "Filter",
  "index": 0,
  "id": "0x103",
  "mask": "0x1FF",
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
  "id": "0x106",
  "mask": "0x1FF",
  "type": "std",
  "status": "Enable"
}
EOS
)

echo "$json"
echo "$json"  | socat - udp-datagram:255.255.255.255:8200,broadcast


