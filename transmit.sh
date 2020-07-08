#!/bin/bash

json=$(cat << EOS
{
  "id": "0x123",
  "type": "stdData",
  "data": [1,2]
}
EOS
)

echo "$json"
echo "$json"  | socat - udp-datagram:255.255.255.255:8200,broadcast

json=$(cat << EOS
{
  "id": "0x123",
  "type": "extData",
  "data": [11,12,13,14]
}
EOS
)

echo "$json"
echo "$json"  | socat - udp-datagram:255.255.255.255:8200,broadcast

json=$(cat << EOS
{
  "id": "0x123",
  "type": "stdRemote"
}
EOS
)

echo "$json"
echo "$json"  | socat - udp-datagram:255.255.255.255:8200,broadcast

json=$(cat << EOS
{
  "id": "0x123",
  "type": "extRemote"
}
EOS
)

echo "$json"
echo "$json"  | socat - udp-datagram:255.255.255.255:8200,broadcast
