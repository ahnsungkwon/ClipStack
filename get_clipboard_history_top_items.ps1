param(
    [int]$Count = 3,
    [string]$OutputPath
)

$ErrorActionPreference = 'Stop'
$sep = '~~~CLIPBOARD_TRIPLETS_SEP~~~'

Add-Type -AssemblyName System.Runtime.WindowsRuntime
$null = [Windows.ApplicationModel.DataTransfer.Clipboard, Windows.ApplicationModel.DataTransfer, ContentType=WindowsRuntime]
$null = [Windows.ApplicationModel.DataTransfer.ClipboardHistoryItemsResult, Windows.ApplicationModel.DataTransfer, ContentType=WindowsRuntime]
$null = [Windows.ApplicationModel.DataTransfer.ClipboardHistoryItemsResultStatus, Windows.ApplicationModel.DataTransfer, ContentType=WindowsRuntime]

function Convert-WinRtAsyncResult {
    param(
        [Parameter(Mandatory = $true)]
        [object]$AsyncOperation,

        [Parameter(Mandatory = $true)]
        [Type]$ResultType
    )

    $asTaskMethod = [System.WindowsRuntimeSystemExtensions].GetMethods() |
        Where-Object {
            $_.ToString() -eq 'System.Threading.Tasks.Task`1[TResult] AsTask[TResult](Windows.Foundation.IAsyncOperation`1[TResult])'
        } |
        Select-Object -First 1

    $genericMethod = $asTaskMethod.MakeGenericMethod($ResultType)
    $task = $genericMethod.Invoke($null, @($AsyncOperation))
    $task.Wait()
    return $task.Result
}

$result = Convert-WinRtAsyncResult `
    -AsyncOperation ([Windows.ApplicationModel.DataTransfer.Clipboard]::GetHistoryItemsAsync()) `
    -ResultType ([Windows.ApplicationModel.DataTransfer.ClipboardHistoryItemsResult])

$items = New-Object System.Collections.Generic.List[string]

if ($result.Status -eq [Windows.ApplicationModel.DataTransfer.ClipboardHistoryItemsResultStatus]::Success) {
    foreach ($historyItem in $result.Items) {
        if ($items.Count -ge $Count) {
            break
        }

        $formats = @($historyItem.Content.AvailableFormats)
        if (-not ($formats -contains [Windows.ApplicationModel.DataTransfer.StandardDataFormats]::Text)) {
            continue
        }

        $text = Convert-WinRtAsyncResult `
            -AsyncOperation ($historyItem.Content.GetTextAsync()) `
            -ResultType ([string])

        if ([string]::IsNullOrWhiteSpace($text)) {
            continue
        }

        $items.Add($text.Trim())
    }
}

$content = [string]::Join("`n$sep`n", $items)
[System.IO.File]::WriteAllText($OutputPath, $content, [System.Text.UTF8Encoding]::new($true))
