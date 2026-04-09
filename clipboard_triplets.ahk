#Requires AutoHotkey v2.0
#SingleInstance Force

global IniPath := A_ScriptDir "\clipboard_triplets.ini"
global HistoryScriptPath := A_ScriptDir "\get_clipboard_history_top_items.ps1"
global ManagerGui := ""

ShowStartupTip()

^!0::OpenManager()

^!1::InjectSet(1)
^!2::InjectSet(2)
^!3::InjectSet(3)
^!4::InjectSet(4)
^!5::InjectSet(5)
^!6::InjectSet(6)

^!+1::OpenManager(1)
^!+2::OpenManager(2)
^!+3::OpenManager(3)
^!+4::OpenManager(4)
^!+5::OpenManager(5)
^!+6::OpenManager(6)

if A_Args.Length >= 1 && A_Args[1] = "--open-manager" {
    SetTimer(OpenManagerOnStartup, -10)
}

ShowStartupTip() {
    TrayTip("클립보드 3종 세트", "Ctrl+Alt+0 관리창 | Ctrl+Alt+1..6 불러오기 | Ctrl+Alt+Shift+1..6 편집")
}

OpenManagerOnStartup() {
    OpenManager()
}

OpenManager(selectedSlot := 1) {
    global ManagerGui

    if IsObject(ManagerGui) {
        try ManagerGui.Destroy()
    }

    windowObj := Gui("+AlwaysOnTop", "클립보드 3종 세트")
    ManagerGui := windowObj
    windowObj.SetFont("s10", "맑은 고딕")
    windowObj.OnEvent("Close", CloseManagerGui)
    windowObj.OnEvent("Escape", CloseManagerGui)

    slotItems := []
    Loop 6 {
        slotItems.Push(A_Index)
    }

    windowObj.AddText("xm", "슬롯")
    slotDrop := windowObj.AddDropDownList("x+10 w80 Choose" selectedSlot, slotItems)
    loadBtn := windowObj.AddButton("x+10 w90", "불러오기")
    saveBtn := windowObj.AddButton("x+10 w90", "저장")
    injectBtn := windowObj.AddButton("x+10 w90", "주입")

    windowObj.AddText("xm y+16", "세트 이름")
    nameEdit := windowObj.AddEdit("x+10 w560")

    windowObj.AddText("xm y+16", "위 항목 (Win+V에서 맨 위)")
    topEdit := windowObj.AddEdit("x+10 w720 r2")

    windowObj.AddText("xm y+16", "가운데 항목")
    middleEdit := windowObj.AddEdit("x+10 w720 r2")

    windowObj.AddText("xm y+16", "아래 항목")
    bottomEdit := windowObj.AddEdit("x+10 w720 r4")

    importHistoryBtn := windowObj.AddButton("xm y+14 w190", "최근 3개 가져오기")
    importCurrentBtn := windowObj.AddButton("x+10 w190", "현재 3줄 가져오기")
    windowObj.AddText("xm y+12 w900"
        , "최근 3개 가져오기는 Win+V 최근 3개 텍스트 항목을 채웁니다. 현재 3줄 가져오기는 현재 클립보드 안의 3줄 텍스트를 채웁니다.")

    windowObj.AddText("xm y+16 w900"
        , "단축키: Ctrl+Alt+1..6 불러오기 | Ctrl+Alt+Shift+1..6 편집. Win+V는 최신 항목이 맨 위에 오므로, 이 스크립트는 아래 -> 가운데 -> 위 순서로 주입합니다.")

    slotDrop.OnEvent("Change", (*) => FillForm(slotDrop.Text + 0, nameEdit, topEdit, middleEdit, bottomEdit))
    loadBtn.OnEvent("Click", (*) => FillForm(slotDrop.Text + 0, nameEdit, topEdit, middleEdit, bottomEdit))
    saveBtn.OnEvent("Click", (*) => SaveForm(slotDrop.Text + 0, nameEdit, topEdit, middleEdit, bottomEdit))
    injectBtn.OnEvent("Click", (*) => SaveAndInject(slotDrop.Text + 0, nameEdit, topEdit, middleEdit, bottomEdit))
    importHistoryBtn.OnEvent("Click", (*) => ImportRecentHistoryItems(topEdit, middleEdit, bottomEdit))
    importCurrentBtn.OnEvent("Click", (*) => ImportCurrentClipboardLines(topEdit, middleEdit, bottomEdit))

    windowObj.Show()
    FillForm(selectedSlot, nameEdit, topEdit, middleEdit, bottomEdit)
}

CloseManagerGui(windowObj, *) {
    global ManagerGui
    try windowObj.Destroy()
    ManagerGui := ""
}

ReadSlot(slot) {
    section := "Slot" slot
    return Map(
        "Name", IniRead(IniPath, section, "Name", ""),
        "Top", IniRead(IniPath, section, "Top", ""),
        "Middle", IniRead(IniPath, section, "Middle", ""),
        "Bottom", IniRead(IniPath, section, "Bottom", "")
    )
}

WriteSlot(slot, name, top, middle, bottom) {
    section := "Slot" slot
    IniWrite(name, IniPath, section, "Name")
    IniWrite(top, IniPath, section, "Top")
    IniWrite(middle, IniPath, section, "Middle")
    IniWrite(bottom, IniPath, section, "Bottom")
}

FillForm(slot, nameEdit, topEdit, middleEdit, bottomEdit) {
    data := ReadSlot(slot)
    nameEdit.Value := data["Name"]
    topEdit.Value := data["Top"]
    middleEdit.Value := data["Middle"]
    bottomEdit.Value := data["Bottom"]
}

SaveForm(slot, nameEdit, topEdit, middleEdit, bottomEdit) {
    WriteSlot(slot, nameEdit.Value, topEdit.Value, middleEdit.Value, bottomEdit.Value)
    ShowTool(slot "번 슬롯 저장됨")
}

SaveAndInject(slot, nameEdit, topEdit, middleEdit, bottomEdit) {
    SaveForm(slot, nameEdit, topEdit, middleEdit, bottomEdit)
    InjectSet(slot)
}

ImportRecentHistoryItems(topEdit, middleEdit, bottomEdit) {
    global HistoryScriptPath

    if !FileExist(HistoryScriptPath) {
        MsgBox("히스토리 읽기 스크립트를 찾을 수 없습니다.`n" HistoryScriptPath)
        return
    }

    outPath := A_Temp "\clipboard_triplets_history.txt"
    try FileDelete(outPath)

    cmd := 'powershell.exe -Sta -NoProfile -ExecutionPolicy Bypass -File "' HistoryScriptPath '" -Count 3 -OutputPath "' outPath '"'
    exitCode := RunWait(cmd, , "Hide")
    if exitCode != 0 {
        MsgBox("멀티클립보드 최근 3개를 읽지 못했습니다.")
        return
    }

    if !FileExist(outPath) {
        MsgBox("히스토리 결과 파일이 생성되지 않았습니다.")
        return
    }

    content := FileRead(outPath, "UTF-8")
    content := StrReplace(content, "`r`n", "`n")
    sep := "~~~CLIPBOARD_TRIPLETS_SEP~~~"
    items := StrSplit(content, "`n" sep "`n")

    cleanItems := []
    for _, item in items {
        if item != "" {
            cleanItems.Push(item)
        }
    }

    if cleanItems.Length < 1 {
        MsgBox("Win+V 최근 텍스트 항목이 없습니다.")
        return
    }

    recentLines := GetNonEmptyLines(cleanItems[1])
    if recentLines.Length = 3 {
        topEdit.Value := recentLines[1]
        middleEdit.Value := recentLines[2]
        bottomEdit.Value := recentLines[3]
        ShowTool("최근 항목의 3줄 가져옴")
        return
    }

    if cleanItems.Length < 3 {
        MsgBox("Win+V 최근 텍스트 항목이 3개보다 적습니다.")
        return
    }

    topEdit.Value := cleanItems[1]
    middleEdit.Value := cleanItems[2]
    bottomEdit.Value := cleanItems[3]
    ShowTool("최근 3개 항목 가져옴")
}

ImportCurrentClipboardLines(topEdit, middleEdit, bottomEdit) {
    text := A_Clipboard
    if text = "" {
        MsgBox("현재 클립보드가 비어 있습니다.")
        return
    }

    lines := GetNonEmptyLines(text)

    if lines.Length != 3 {
        MsgBox("현재 클립보드에는 비어 있지 않은 3줄이 정확히 있어야 합니다.")
        return
    }

    topEdit.Value := lines[1]
    middleEdit.Value := lines[2]
    bottomEdit.Value := lines[3]
    ShowTool("현재 3줄 가져옴")
}

GetNonEmptyLines(text) {
    lines := []
    for _, line in StrSplit(text, "`n", "`r") {
        trimmed := Trim(line)
        if trimmed != "" {
            lines.Push(trimmed)
        }
    }
    return lines
}

InjectSet(slot) {
    data := ReadSlot(slot)
    if Trim(data["Top"]) = "" || Trim(data["Middle"]) = "" || Trim(data["Bottom"]) = "" {
        MsgBox(slot "번 슬롯이 비어 있거나 덜 채워져 있습니다.")
        return
    }

    title := Trim(data["Name"])
    if title = "" {
        title := slot "번 슬롯"
    }

    items := [data["Bottom"], data["Middle"], data["Top"]]
    for index, item in items {
        if !PushClipboardItem(item, index = items.Length) {
            MsgBox("클립보드에 항목을 넣는 중 문제가 생겼습니다. 다시 한 번 시도해 주세요.")
            return
        }
    }

    ShowTool(title " 불러옴")
}

PushClipboardItem(item, isLast := false) {
    A_Clipboard := ""
    Sleep(120)

    A_Clipboard := item
    if !ClipWait(1) {
        return false
    }

    if A_Clipboard != item {
        Sleep(150)
    }

    Sleep(isLast ? 450 : 700)
    return true
}

ShowTool(message) {
    ToolTip(message)
    SetTimer(HideTool, -1200)
}

HideTool() {
    ToolTip()
}
