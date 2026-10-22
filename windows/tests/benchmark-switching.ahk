#Requires AutoHotkey v2.0
#Include %A_ScriptDir%\..\src\windowSwitcher.ahk

; Run manually: opens four disposable test windows, never clicks in Dofus.
reportPath := A_Args.Length ? A_Args[1] : A_Temp "\dofusahk-switching.csv"
testWindows := []
report := "Mode,Iteration,Target,RequestMs,FocusMs,Focused`n"
exitCode := 0
frequency := 0
DllCall("QueryPerformanceFrequency", "Int64*", &frequency)

NowMs() {
    global frequency
    counter := 0
    DllCall("QueryPerformanceCounter", "Int64*", &counter)
    return counter * 1000 / frequency
}

try {
    Loop 4 {
        window := Gui(, "DofusAHK benchmark " A_TickCount " account " A_Index)
        window.AddText(, "Temporary focus test - account " A_Index)
        window.Show("x200 y200 w360 h100")
        testWindows.Push(window)
    }

    ; This exercises both the first lookup and the cached-handle path.
    for mode in ["WinActivate", "NativeWithFallback"] {
        Loop 10 {
            iteration := A_Index
            for index, window in testWindows {
                started := NowMs()
                if mode = "WinActivate"
                    WinActivate(window.Hwnd)
                else
                    ActivateWindow(window.Title)
                returned := NowMs()
                ; Measure confirmation separately from the request duration.
                focused := !!WinActive(window.Hwnd)
                while !focused && NowMs() - started < 250 {
                    Sleep(1)
                    focused := !!WinActive(window.Hwnd)
                }
                elapsed := NowMs() - started
                report .= Format("{},{},{},{:.3f},{:.3f},{}`n",
                    mode, iteration, index, returned - started, elapsed, focused)
                if !focused
                    throw Error("A test window did not become active within 250 ms.")
            }
        }
    }

    isScriptEnabled := false
    before := WinExist("A")
    ActivateWindow(testWindows[1].Title)
    if WinExist("A") != before
        throw Error("Disabled switching changed focus.")
    isScriptEnabled := true
    if ActivateWindow("DofusAHK nonexistent " A_TickCount)
        throw Error("A missing window was reported as activated.")

    ; Check restore and a closed window previously held in the cache.
    last := testWindows[4]
    title := last.Title
    WinMinimize(last.Hwnd)
    ActivateWindow(title)
    if !WinWaitActive(last.Hwnd, , 1) || WinGetMinMax(last.Hwnd) = -1
        throw Error("Minimized window was not restored.")
    last.Destroy()
    testWindows.Pop()
    if ActivateWindow(title)
        throw Error("A destroyed window was reported as activated.")
} catch Error as err {
    report .= "ERROR: " StrReplace(err.Message, "`n", " ") "`n"
    exitCode := 1
} finally {
    for window in testWindows
        window.Destroy()
    FileAppend(report, reportPath, "UTF-8")
}
ExitApp(exitCode)
