#!/bin/sh
until python /home/pi/Development/bugs/bugs_behaviour.py; do
    echo "Lamp crashed. Relaunching..."
    sleep 1
done
