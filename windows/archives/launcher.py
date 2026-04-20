#!/usr/bin/env python3
# coding: utf-8

import os

filename = input("Please enter file name : ")
characters = ["Baabu", "Melina", "Takamori", "Sanguor"]
playing_order = [4, 1, 2, 3]

user = os.getlogin()
# dofus_path = f"C:/Users/{user}/AppData/Local/Ankama/Dofus/VERSION"
dofus_path = f"C:/Users/Paul Le Bras/AppData/Local/Ankama/zaap/dofus/VERSION"
f = open(dofus_path, "r")
lines = f.readlines()
version = lines[0][:-1]


# hotkeys = ['!&', '!é', '!\"', '!\'', '!(', '!-', '!è', '!_', '!ç']
hotkeys = ['&', 'é', '\"', '\'', '(', '-', 'è', '_', 'ç']


start = f"""#NoEnv ; Recommended for performance and compatibility with future AutoHotkey releases.
; #Warn  ; Enable warnings to assist with detecting common errors.
SendMode Input ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir% ; Ensures a consistent starting directory.

if WinExist("Ankama Launcher")
    WinActivate
else
    Run "C:\Program Files\Ankama\Ankama Launcher\Ankama Launcher.exe"

WinWait, Ankama Launcher
loop {{
    Sleep, 50
    PixelGetColor, color, 256, 169
}} until color = 0x4BCCB1


Send ^{{{hotkeys[len(characters) - 1][-1]}}}

Process, Exist, Ankama Launcher.exe
If ErrorLevel = 0
{{
    Return
}}
Else
{{
"""

middle = ''
for i in range(0, len(playing_order)):
    middle += (f'    {hotkeys[i]}::\n'
               f'        WinActivate, {characters[playing_order[i] - 1]} - Dofus {version}\n'
               '    return\n')

end = (
    '}\n'
    'Return'
)

# print('middle =', middle)

content = start + middle + end

with open(f'{filename}.ahk', 'w') as f:
    f.write(content)
