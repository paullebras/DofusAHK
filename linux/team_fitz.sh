#!/bin/bash

version=$(cat /home/plebras/.config/Ankama/Dofus/VERSION)

case $1 in
    "F1")
        xdotool search --name "Baabu - Dofus $version" windowactivate
        xdotool search --name "Eni-dolma - Dofus $version" windowactivate
        xdotool search --name "Eni-dolma-deux - Dofus $version" windowactivate
        xdotool search --name "Eni-dolma-trois - Dofus $version" windowactivate
        xdotool search --name "Eni-dolma-quatre - Dofus $version" windowactivate
        ;;
    "F2")
        xdotool search --name "Sanguor - Dofus $version" windowactivate
        xdotool search --name "Fitz-Otori - Dofus $version" windowactivate
        xdotool search --name "Hupper-dolma-deux - Dofus $version" windowactivate
        xdotool search --name "Hupper-dolma-trois - Dofus $version" windowactivate
        xdotool search --name "Hupper-dolma-quatre - Dofus $version" windowactivate
        ;;
    "F3")
        xdotool search --name "Takamori - Dofus $version" windowactivate
        xdotool search --name "Sacri-dolma - Dofus $version" windowactivate
        xdotool search --name "Sacri-dolma-deux - Dofus $version" windowactivate
        xdotool search --name "Sacri-dolma-trois - Dofus $version" windowactivate
        xdotool search --name "Sacri-dolma-quatre - Dofus $version" windowactivate
        ;;
    "F4")
        xdotool search --name "Ninomae-inanis - Dofus $version" windowactivate
        xdotool search --name "Steam-dolma - Dofus $version" windowactivate
        xdotool search --name "Steam-dolma-deux - Dofus $version" windowactivate
        xdotool search --name "Steam-dolma-trois - Dofus $version" windowactivate
        xdotool search --name "Steam-dolma-quatre - Dofus $version" windowactivate
        ;;
esac
