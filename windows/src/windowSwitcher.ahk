#Requires AutoHotkey v2.0
#SingleInstance Force
#WinActivateForce
#Warn
SendMode("Input")
SetWorkingDir(A_ScriptDir)
SetTitleMatchMode(2)
; Do not keep a switching hotkey busy for AHK's default 100 ms after activation.
SetWinDelay(-1)

isScriptEnabled := true

ActivateWindow(winTitle) {
    global isScriptEnabled
    if !isScriptEnabled
        return
    hwnd := WinExist(winTitle)
    if hwnd {
        try {
            WinActivate(hwnd)
        } catch TargetError {
            ; The window may have closed after WinExist.
            return
        }
    }
}

F12:: {
    global isScriptEnabled
    isScriptEnabled := !isScriptEnabled
}

F1:: ActivateWindow("Baabu")
F2:: ActivateWindow("Sanguor")
F3:: ActivateWindow("Takamori")
F4:: ActivateWindow("Ninomae-inanis")
