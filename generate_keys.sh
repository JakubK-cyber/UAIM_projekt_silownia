#!/bin/sh

openssl ecparam -genkey -name secp256r1 -out /silownia_api/priv.key
chmod 600 /silownia_api/priv.key
openssl ec -in /silownia_api/priv.key -pubout -out /silownia_api/pub.key