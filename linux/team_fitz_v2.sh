#!/bin/bash

mapfile -t window_ids < <(xdotool search --class "Dofus.x64" | sort -n)

case $1 in
    "F1")
        xdotool windowactivate "${window_ids[0]}"
        ;;
    "F2")
        xdotool windowactivate "${window_ids[1]}"
        ;;
    "F3")
        xdotool windowactivate "${window_ids[2]}"
        ;;
    "F4")
        xdotool windowactivate "${window_ids[3]}"
        ;;
    "F5")
        xdotool windowactivate "${window_ids[4]}"
        ;;
esac