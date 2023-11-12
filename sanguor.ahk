#NoEnv ; Recommended for performance and compatibility with future AutoHotkey releases.
; #Warn  ; Enable warnings to assist with detecting common errors.
SendMode Input ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir% ; Ensures a consistent starting directory.

isScriptEnabled := 1

file := FileOpen("C:\Users\Paul Le Bras\AppData\Local\Ankama\Dofus", "r")
dofusVersion := ""
FileRead, dofusVersion, %file%
file.Close()

ActivateWindow(winTitle, isScriptEnabled, dofusVersion)
{
    If isScriptEnabled
    {
        WinActivate, %winTitle% - %dofusVersion%
    }
}

F12::
    isScriptEnabled := !isScriptEnabled
return

F1::
    ActivateWindow("Baabu", isScriptEnabled, dofusVersion)
return
F2::
    ActivateWindow("Sanguor", isScriptEnabled, dofusVersion)
return
F3::
    ActivateWindow("Takamori", isScriptEnabled, dofusVersion)
return
F4::
    ActivateWindow("Melina-[Jul]", isScriptEnabled, dofusVersion)
return

