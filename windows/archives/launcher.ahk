#NoEnv ; Recommended for performance and compatibility with future AutoHotkey releases.
; #Warn  ; Enable warnings to assist with detecting common errors.
SendMode Input ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir% ; Ensures a consistent starting directory.

if WinExist("Ankama Launcher")
    WinActivate
else
    Run "C:\Program Files\Ankama\Ankama Launcher\Ankama Launcher.exe"

WinWait, Ankama Launcher
loop {
    Sleep, 50
    PixelGetColor, color, 256, 169
} until color = 0x4BCCB1


Send ^{'}

Process, Exist, Ankama Launcher.exe
If ErrorLevel = 0
{
    Return
}
Else
{
    !&::
        WinActivate, Takamori - Dofus 2.65.5.16
    return
    !é::
        WinActivate, Melina - Dofus 2.65.5.16
    return
    !"::
        WinActivate, Baabu - Dofus 2.65.5.16
    return
    !'::
        WinActivate, Sanguor - Dofus 2.65.5.16
    return
}
Return