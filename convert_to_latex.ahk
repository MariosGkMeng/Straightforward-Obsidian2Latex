; Initialize a flag to check if Alt + E was pressed
AltE_Flag := false

!e::
    ; Check if Alt + E was pressed recently
    if (AltE_Flag) {
        ; Perform action for Alt + E + E
        AltE_Flag := false ; Reset the flag
        ; MsgBox, You pressed Alt + E + E!
        Run, C:\Users\mariosg\OneDrive - NTNU\FILES\AUTOMATIONS\convert_to_latex.bat, C:\Users\mariosg\OneDrive - NTNU\FILES\AUTOMATIONS
    } else {
        ; Set the flag and start a timer
        AltE_Flag := true
        SetTimer, ResetAltEFlag, -500 ; 500 ms to press 'E' again
    }
    return

ResetAltEFlag:
    AltE_Flag := false
    return
