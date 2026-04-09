#Requires AutoHotkey v2.0
#SingleInstance Force

; ===== MULTILINGUAL SUPPORT (다국어 지원) =====
langs := Map(
    "en", Map(
        "title", "Clipboard Triplets",
        "slot", "Slot",
        "load", "Load",
        "save", "Save",
        "inject", "Inject",
        "settings", "Settings",
        "language", "Language",
        "setname", "Set Name",
        "top", "Top Item (appears at top in Win+V)",
        "middle", "Middle Item",
        "bottom", "Bottom Item",
        "import_history", "Import Latest 3",
        "import_current", "Import Current 3 Lines",
        "import_history_desc", "Import Latest 3 fills the top 3 items from Win+V history. Import Current 3 Lines fills 3 non-empty lines from current clipboard.",
        "hotkey_desc", "Hotkeys: Ctrl+Alt+1..6 Load | Ctrl+Alt+Shift+1..6 Edit. Since Win+V shows latest at top, items are injected in reverse order: bottom → middle → top.",
        "slot_saved", "Slot saved",
        "recent_3_loaded", "Loaded latest 3 lines",
        "recent_3_items_loaded", "Loaded latest 3 items",
        "current_3_loaded", "Loaded current 3 lines",
        "set_loaded", "Loaded",
        "startup_tip", "Ctrl+Alt+0 Manager | Ctrl+Alt+1..6 Load | Ctrl+Alt+Shift+1..6 Edit",
        "language_changed", "Language changed. Restart to apply changes.",
        "err_script_not_found", "History script not found.",
        "err_clipboard_read", "Failed to read clipboard history.",
        "err_output_not_created", "Output file was not created.",
        "err_no_items", "No text items in Win+V history.",
        "err_not_enough_items", "Fewer than 3 items in Win+V history.",
        "err_clipboard_empty", "Clipboard is empty.",
        "err_not_3_lines", "Clipboard must have exactly 3 non-empty lines.",
        "err_slot_empty", "Slot is empty or incomplete.",
        "err_clipboard_inject", "Problem injecting items to clipboard. Please try again."
    ),
    "ko", Map(
        "title", "클립보드 3종 세트",
        "slot", "슬롯",
        "load", "불러오기",
        "save", "저장",
        "inject", "주입",
        "settings", "설정",
        "language", "언어",
        "setname", "세트 이름",
        "top", "위 항목 (Win+V에서 맨 위)",
        "middle", "가운데 항목",
        "bottom", "아래 항목",
        "import_history", "최근 3개 가져오기",
        "import_current", "현재 3줄 가져오기",
        "import_history_desc", "최근 3개 가져오기는 Win+V 최근 3개 텍스트 항목을 채웁니다. 현재 3줄 가져오기는 현재 클립보드 안의 3줄 텍스트를 채웁니다.",
        "hotkey_desc", "단축키: Ctrl+Alt+1..6 불러오기 | Ctrl+Alt+Shift+1..6 편집. Win+V는 최신 항목이 맨 위에 오므로, 이 스크립트는 아래 -> 가운데 -> 위 순서로 주입합니다.",
        "slot_saved", "번 슬롯 저장됨",
        "recent_3_loaded", "최근 항목의 3줄 가져옴",
        "recent_3_items_loaded", "최근 3개 항목 가져옴",
        "current_3_loaded", "현재 3줄 가져옴",
        "set_loaded", "불러옴",
        "startup_tip", "Ctrl+Alt+0 관리창 | Ctrl+Alt+1..6 불러오기 | Ctrl+Alt+Shift+1..6 편집",
        "language_changed", "언어가 변경되었습니다. 재시작 후 적용됩니다.",
        "err_script_not_found", "히스토리 읽기 스크립트를 찾을 수 없습니다.",
        "err_clipboard_read", "멀티클립보드 최근 3개를 읽지 못했습니다.",
        "err_output_not_created", "히스토리 결과 파일이 생성되지 않았습니다.",
        "err_no_items", "Win+V 최근 텍스트 항목이 없습니다.",
        "err_not_enough_items", "Win+V 최근 텍스트 항목이 3개보다 적습니다.",
        "err_clipboard_empty", "현재 클립보드가 비어 있습니다.",
        "err_not_3_lines", "현재 클립보드에는 비어 있지 않은 3줄이 정확히 있어야 합니다.",
        "err_slot_empty", "번 슬롯이 비어 있거나 덜 채워져 있습니다.",
        "err_clipboard_inject", "클립보드에 항목을 넣는 중 문제가 생겼습니다. 다시 한 번 시도해 주세요."
    ),
    "es", Map(
        "title", "Portapapeles Trillizos",
        "slot", "Ranura",
        "load", "Cargar",
        "save", "Guardar",
        "inject", "Inyectar",
        "settings", "Configuración",
        "language", "Idioma",
        "setname", "Nombre del conjunto",
        "top", "Elemento superior",
        "middle", "Elemento medio",
        "bottom", "Elemento inferior",
        "import_history", "Importar 3 últimos",
        "import_current", "Importar 3 líneas actuales",
        "import_history_desc", "Importar 3 últimos rellena los 3 elementos superiores del historial Win+V. Importar 3 líneas actuales rellena 3 líneas no vacías del portapapeles actual.",
        "hotkey_desc", "Atajos: Ctrl+Alt+1..6 Cargar | Ctrl+Alt+Shift+1..6 Editar. Como Win+V muestra lo más reciente arriba, los elementos se inyectan en orden inverso: inferior → medio → superior.",
        "slot_saved", "Ranura guardada",
        "recent_3_loaded", "Cargadas 3 líneas más recientes",
        "recent_3_items_loaded", "Cargados 3 elementos más recientes",
        "current_3_loaded", "Cargadas 3 líneas actuales",
        "set_loaded", "Cargado",
        "startup_tip", "Ctrl+Alt+0 Administrador | Ctrl+Alt+1..6 Cargar | Ctrl+Alt+Shift+1..6 Editar",
        "language_changed", "Idioma cambiado. Reinicia para aplicar cambios.",
        "err_script_not_found", "Script de historial no encontrado.",
        "err_clipboard_read", "No se pudo leer el historial del portapapeles.",
        "err_output_not_created", "El archivo de salida no se creó.",
        "err_no_items", "Sin elementos de texto en el historial Win+V.",
        "err_not_enough_items", "Menos de 3 elementos en el historial Win+V.",
        "err_clipboard_empty", "El portapapeles está vacío.",
        "err_not_3_lines", "El portapapeles debe tener exactamente 3 líneas no vacías.",
        "err_slot_empty", "La ranura está vacía o incompleta.",
        "err_clipboard_inject", "Problema al inyectar elementos en el portapapeles. Por favor, intenta de nuevo."
    ),
    "fr", Map(
        "title", "Presse-papiers Triplets",
        "slot", "Emplacement",
        "load", "Charger",
        "save", "Enregistrer",
        "inject", "Injecter",
        "settings", "Paramètres",
        "language", "Langue",
        "setname", "Nom de l'ensemble",
        "top", "Élément supérieur",
        "middle", "Élément du milieu",
        "bottom", "Élément inférieur",
        "import_history", "Importer 3 derniers",
        "import_current", "Importer 3 lignes actuelles",
        "import_history_desc", "Importer 3 derniers remplit les 3 éléments supérieurs de l'historique Win+V. Importer 3 lignes actuelles remplit 3 lignes non vides du presse-papiers actuel.",
        "hotkey_desc", "Raccourcis: Ctrl+Alt+1..6 Charger | Ctrl+Alt+Shift+1..6 Éditer. Comme Win+V affiche le plus récent en haut, les éléments sont injectés dans l'ordre inverse: inférieur → milieu → supérieur.",
        "slot_saved", "Emplacement enregistré",
        "recent_3_loaded", "3 lignes les plus récentes chargées",
        "recent_3_items_loaded", "3 derniers éléments chargés",
        "current_3_loaded", "3 lignes actuelles chargées",
        "set_loaded", "Chargé",
        "startup_tip", "Ctrl+Alt+0 Gestionnaire | Ctrl+Alt+1..6 Charger | Ctrl+Alt+Shift+1..6 Éditer",
        "language_changed", "Langue modifiée. Redémarrez pour appliquer les modifications.",
        "err_script_not_found", "Script d'historique non trouvé.",
        "err_clipboard_read", "Impossible de lire l'historique du presse-papiers.",
        "err_output_not_created", "Le fichier de sortie n'a pas été créé.",
        "err_no_items", "Aucun élément de texte dans l'historique Win+V.",
        "err_not_enough_items", "Moins de 3 éléments dans l'historique Win+V.",
        "err_clipboard_empty", "Le presse-papiers est vide.",
        "err_not_3_lines", "Le presse-papiers doit contenir exactement 3 lignes non vides.",
        "err_slot_empty", "L'emplacement est vide ou incomplet.",
        "err_clipboard_inject", "Problème lors de l'injection d'éléments dans le presse-papiers. Veuillez réessayer."
    ),
    "de", Map(
        "title", "Zwischenablage Triplets",
        "slot", "Feld",
        "load", "Laden",
        "save", "Speichern",
        "inject", "Injizieren",
        "settings", "Einstellungen",
        "language", "Sprache",
        "setname", "Satzname",
        "top", "Oberes Element",
        "middle", "Mittleres Element",
        "bottom", "Unteres Element",
        "import_history", "Letzte 3 importieren",
        "import_current", "Aktuelle 3 Zeilen importieren",
        "import_history_desc", "Letzte 3 importieren füllt die 3 oberen Elemente aus Win+V-Verlauf. Aktuelle 3 Zeilen importieren füllt 3 nicht leere Zeilen aus der aktuellen Zwischenablage.",
        "hotkey_desc", "Tastenkombinationen: Strg+Alt+1..6 Laden | Strg+Alt+Shift+1..6 Bearbeiten. Da Win+V die neuesten oben anzeigt, werden Elemente in umgekehrter Reihenfolge eingespritzt: unten → Mitte → oben.",
        "slot_saved", "Feld gespeichert",
        "recent_3_loaded", "Letzte 3 Zeilen geladen",
        "recent_3_items_loaded", "Letzte 3 Elemente geladen",
        "current_3_loaded", "Aktuelle 3 Zeilen geladen",
        "set_loaded", "Geladen",
        "startup_tip", "Strg+Alt+0 Manager | Strg+Alt+1..6 Laden | Strg+Alt+Shift+1..6 Bearbeiten",
        "language_changed", "Sprache geändert. Starten Sie neu, um Änderungen anzuwenden.",
        "err_script_not_found", "Verlaufsskript nicht gefunden.",
        "err_clipboard_read", "Verlauf der Zwischenablage konnte nicht gelesen werden.",
        "err_output_not_created", "Ausgabedatei wurde nicht erstellt.",
        "err_no_items", "Keine Textelemente im Win+V-Verlauf.",
        "err_not_enough_items", "Weniger als 3 Elemente im Win+V-Verlauf.",
        "err_clipboard_empty", "Zwischenablage ist leer.",
        "err_not_3_lines", "Zwischenablage muss genau 3 nicht leere Zeilen haben.",
        "err_slot_empty", "Feld ist leer oder unvollständig.",
        "err_clipboard_inject", "Problem beim Injizieren von Elementen in die Zwischenablage. Bitte versuchen Sie es erneut."
    )
)

; Language detection & initialization
GetCurrentLanguage() {
    savedLang := IniRead(A_ScriptDir "\clipboard_triplets.ini", "Settings", "Language", "")
    if (savedLang != "" && langs.Has(savedLang))
        return savedLang

    sysLang := A_Language
    if (sysLang = "0412")
        return "ko"
    else
        return "en"
}

global IniPath := A_ScriptDir "\clipboard_triplets.ini"
global HistoryScriptPath := A_ScriptDir "\get_clipboard_history_top_items.ps1"
global ManagerGui := ""
global currentLang := GetCurrentLanguage()
global lang := langs[currentLang]

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
    TrayTip(lang["title"], "Ctrl+Alt+0 " lang["startup_tip"])
}

OpenManagerOnStartup() {
    OpenManager()
}

ChangeLanguage(newLang) {
    global currentLang, lang

    if !langs.Has(newLang)
        return

    currentLang := newLang
    lang := langs[currentLang]
    IniWrite(newLang, IniPath, "Settings", "Language")
    MsgBox(lang["language_changed"])
}

OpenManager(selectedSlot := 1) {
    global ManagerGui

    if IsObject(ManagerGui) {
        try ManagerGui.Destroy()
    }

    windowObj := Gui("+AlwaysOnTop", lang["title"])
    ManagerGui := windowObj
    windowObj.SetFont("s10", "맑은 고딕")
    windowObj.OnEvent("Close", CloseManagerGui)
    windowObj.OnEvent("Escape", CloseManagerGui)

    slotItems := []
    Loop 6 {
        slotItems.Push(A_Index)
    }

    langItems := ["English", "한국어", "Español", "Français", "Deutsch"]
    langValues := ["en", "ko", "es", "fr", "de"]
    currentLangIndex := langValues.IndexOf(currentLang) || 1

    windowObj.AddText("xm", lang["slot"])
    slotDrop := windowObj.AddDropDownList("x+10 w80 Choose" selectedSlot, slotItems)
    loadBtn := windowObj.AddButton("x+10 w90", lang["load"])
    saveBtn := windowObj.AddButton("x+10 w90", lang["save"])
    injectBtn := windowObj.AddButton("x+10 w90", lang["inject"])

    windowObj.AddText("xm y+16", lang["language"])
    langDrop := windowObj.AddDropDownList("x+10 w140 Choose" currentLangIndex, langItems)
    settingsBtn := windowObj.AddButton("x+10 w90", lang["settings"])

    windowObj.AddText("xm y+16", lang["setname"])
    nameEdit := windowObj.AddEdit("x+10 w560")

    windowObj.AddText("xm y+16", lang["top"])
    topEdit := windowObj.AddEdit("x+10 w720 r2")

    windowObj.AddText("xm y+16", lang["middle"])
    middleEdit := windowObj.AddEdit("x+10 w720 r2")

    windowObj.AddText("xm y+16", lang["bottom"])
    bottomEdit := windowObj.AddEdit("x+10 w720 r4")

    importHistoryBtn := windowObj.AddButton("xm y+14 w190", lang["import_history"])
    importCurrentBtn := windowObj.AddButton("x+10 w190", lang["import_current"])
    windowObj.AddText("xm y+12 w900", lang["import_history_desc"])
    windowObj.AddText("xm y+16 w900", lang["hotkey_desc"])

    slotDrop.OnEvent("Change", (*) => FillForm(slotDrop.Text + 0, nameEdit, topEdit, middleEdit, bottomEdit))
    loadBtn.OnEvent("Click", (*) => FillForm(slotDrop.Text + 0, nameEdit, topEdit, middleEdit, bottomEdit))
    saveBtn.OnEvent("Click", (*) => SaveForm(slotDrop.Text + 0, nameEdit, topEdit, middleEdit, bottomEdit))
    injectBtn.OnEvent("Click", (*) => SaveAndInject(slotDrop.Text + 0, nameEdit, topEdit, middleEdit, bottomEdit))
    langDrop.OnEvent("Change", (*) => ChangeLanguage(langValues[langDrop.Value]))
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
    ShowTool(slot lang["slot_saved"])
}

SaveAndInject(slot, nameEdit, topEdit, middleEdit, bottomEdit) {
    SaveForm(slot, nameEdit, topEdit, middleEdit, bottomEdit)
    InjectSet(slot)
}

ImportRecentHistoryItems(topEdit, middleEdit, bottomEdit) {
    global HistoryScriptPath

    if !FileExist(HistoryScriptPath) {
        MsgBox(lang["err_script_not_found"] "`n" HistoryScriptPath)
        return
    }

    outPath := A_Temp "\clipboard_triplets_history.txt"
    try FileDelete(outPath)

    cmd := 'powershell.exe -Sta -NoProfile -ExecutionPolicy Bypass -File "' HistoryScriptPath '" -Count 3 -OutputPath "' outPath '"'
    exitCode := RunWait(cmd, , "Hide")
    if exitCode != 0 {
        MsgBox(lang["err_clipboard_read"])
        return
    }

    if !FileExist(outPath) {
        MsgBox(lang["err_output_not_created"])
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
        MsgBox(lang["err_no_items"])
        return
    }

    recentLines := GetNonEmptyLines(cleanItems[1])
    if recentLines.Length = 3 {
        topEdit.Value := recentLines[1]
        middleEdit.Value := recentLines[2]
        bottomEdit.Value := recentLines[3]
        ShowTool(lang["recent_3_loaded"])
        return
    }

    if cleanItems.Length < 3 {
        MsgBox(lang["err_not_enough_items"])
        return
    }

    topEdit.Value := cleanItems[1]
    middleEdit.Value := cleanItems[2]
    bottomEdit.Value := cleanItems[3]
    ShowTool(lang["recent_3_items_loaded"])
}

ImportCurrentClipboardLines(topEdit, middleEdit, bottomEdit) {
    text := A_Clipboard
    if text = "" {
        MsgBox(lang["err_clipboard_empty"])
        return
    }

    lines := GetNonEmptyLines(text)

    if lines.Length != 3 {
        MsgBox(lang["err_not_3_lines"])
        return
    }

    topEdit.Value := lines[1]
    middleEdit.Value := lines[2]
    bottomEdit.Value := lines[3]
    ShowTool(lang["current_3_loaded"])
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
        MsgBox(slot lang["err_slot_empty"])
        return
    }

    title := Trim(data["Name"])
    if title = "" {
        title := slot " " lang["slot"]
    }

    items := [data["Bottom"], data["Middle"], data["Top"]]
    for index, item in items {
        if !PushClipboardItem(item, index = items.Length) {
            MsgBox(lang["err_clipboard_inject"])
            return
        }
    }

    ShowTool(title " " lang["set_loaded"])
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
