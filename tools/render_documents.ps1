param([string]$Root = (Split-Path $PSScriptRoot -Parent), [string]$Only = '')
$ErrorActionPreference = 'Stop'
$rootPath = (Resolve-Path -LiteralPath $Root).Path
$qaRoot = Join-Path $rootPath '_qa'
New-Item -ItemType Directory -Path $qaRoot -Force | Out-Null
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
try {
    $files = Get-ChildItem -LiteralPath (Join-Path $rootPath 'labs') -Filter '*.docx' -Recurse
    foreach ($file in $files) {
        if ($file.Name.StartsWith('~$') -or $file.Name -eq 'МУ_ЛР_09.docx') { continue }
        if ($Only -and $file.BaseName -ne $Only) { continue }
        $relative = $file.FullName.Substring($rootPath.Length + 1)
        $name = if ($file.BaseName -eq 'project_brief') { 'project_brief' } else { $file.Directory.Name }
        $folder = Join-Path $qaRoot $name
        New-Item -ItemType Directory -Path $folder -Force | Out-Null
        $pdf = Join-Path $folder 'document.pdf'
        $document = $null
        try {
            $document = $word.Documents.Open($file.FullName, $false, $true)
            $document.Repaginate()
            $pages = $document.ComputeStatistics(2)
            $document.ExportAsFixedFormat($pdf, 17)
            Write-Output "$relative : $pages pages"
        } finally { if ($document) { $document.Close(0) } }
        & 'C:\Users\PC\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\poppler\Library\bin\pdftoppm.exe' -scale-to 1400 -png $pdf (Join-Path $folder 'page')
        if ($LASTEXITCODE -ne 0) { throw "PDF rasterization failed: $relative" }
    }
} finally { $word.Quit() }
