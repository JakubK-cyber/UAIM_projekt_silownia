#!/bin/sh

if [ ! -f "pub.key" ] || [ ! -f "priv.key" ]; then

    sh generate_keys.sh
fi

python3 app.py