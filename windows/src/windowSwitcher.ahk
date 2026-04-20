#NoEnv ; Recommended for performance and compatibility with future AutoHotkey releases.
; #Warn  ; Enable warnings to assist with detecting common errors.
SendMode Input ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir% ; Ensures a consistent starting directory.

isScriptEnabled := 1

if (A_Args.Count() > 0) {
    dofusVersion := A_Args[1]
} else {
    MsgBox, No command line argument provided. Exiting script.
    ExitApp
}

ActivateWindow(winTitle, isScriptEnabled)
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
    ActivateWindow("Baabu", isScriptEnabled)
return
F2::
    ActivateWindow("Sanguor", isScriptEnabled)
return
F3::
    ActivateWindow("Takamori", isScriptEnabled)
return
F4::
    ActivateWindow("Melina-[Jul]", isScriptEnabled)
return
