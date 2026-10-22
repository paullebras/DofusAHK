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
    static windows := Map()
    if !isScriptEnabled
        return false

    try {
        hwnd := windows.Has(winTitle) ? windows[winTitle] : 0
        ; Recheck cached handles: a closed window's handle may be reused.
        if !hwnd || !DllCall("IsWindow", "Ptr", hwnd, "Int")
            || !InStr(WinGetTitle(hwnd), winTitle, true) {
            hwnd := WinExist(winTitle)
            if !hwnd
                return false
            windows[winTitle] := hwnd
        }
        if WinActive(hwnd)
            return true

        ; The normal case needs one native request, without WinActivate's retries.
        ; Keep AHK's restore/activation workarounds for minimized windows or refusal.
        if WinGetMinMax(hwnd) != -1
            && DllCall("SetForegroundWindow", "Ptr", hwnd, "Int")
            return true
        WinActivate(hwnd)
        return !!WinActive(hwnd)
    } catch TargetError {
        ; The window may close between lookup and activation.
        if windows.Has(winTitle)
            windows.Delete(winTitle)
        return false
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
