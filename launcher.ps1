# AI Model Launcher — PowerShell Version
# Lightweight alternative with colored output

$ErrorActionPreference = 'SilentlyContinue'
$ConfigFile = Join-Path $PSScriptRoot "config.txt"
$lastModel = ""
$workDir = $PSScriptRoot

# Load config
if (Test-Path $ConfigFile) {
    Get-Content $ConfigFile | ForEach-Object {
        if ($_ -match "^(.+?)=(.+)$") {
            switch ($Matches[1]) {
                "last_model" { $lastModel = $Matches[2] }
                "work_dir"   { $workDir = $Matches[2] }
            }
        }
    }
}

function Save-Config {
    @("last_model=$lastModel", "work_dir=$workDir") | Set-Content $ConfigFile
}

function Get-Models {
    $raw = ollama list 2>$null
    if (-not $raw) { return @() }
    $lines = $raw | Select-Object -Skip 1 | Sort-Object
    $models = @()
    foreach ($line in $lines) {
        $parts = $line -split '\s+'
        if ($parts.Count -ge 3) {
            $name = $parts[0]
            for ($i = 1; $i -lt $parts.Count; $i++) {
                if ($parts[$i] -match '^\d+\.?\d*$') {
                    $size = $parts[$i]
                    $unit = if ($i + 1 -lt $parts.Count) { $parts[$i + 1] } else { "GB" }
                    $models += [PSCustomObject]@{ Name = $name; Size = "$size $unit" }
                    break
                }
            }
        }
    }
    return $models
}

function Get-Running {
    $raw = ollama ps 2>$null
    if (-not $raw) { return $null }
    $lines = $raw | Select-Object -Skip 1
    foreach ($line in $lines) {
        $parts = $line -split '\s+'
        if ($parts[0]) { return $parts[0] }
    }
    return $null
}

function Show-Menu {
    Clear-Host
    Write-Host "========================================================" -ForegroundColor DarkCyan
    Write-Host "             AI Model Launcher" -ForegroundColor Cyan
    Write-Host "              (PowerShell Edition)" -ForegroundColor DarkGray
    Write-Host "========================================================" -ForegroundColor DarkCyan
    Write-Host ""

    # Running model
    $running = Get-Running
    if ($running) {
        Write-Host " [*] Running: " -NoNewline -ForegroundColor Green
        Write-Host $running -ForegroundColor White
    } else {
        Write-Host " [*] Running: (none)" -ForegroundColor DarkGray
    }

    # GPU
    try {
        $gpu = nvidia-smi --query-gpu=memory.used,memory.total,utilization.gpu --format=csv,noheader,nounits 2>$null
        if ($gpu) {
            $p = $gpu -split ',\s*'
            Write-Host " [#] GPU: $($p[0])/$($p[1]) MB ($($p[2])%)" -ForegroundColor Yellow
        }
    } catch {}

    # RAM
    try {
        $os = Get-CimInstance Win32_OperatingSystem
        $free = [math]::Round($os.FreePhysicalMemory / 1MB, 1)
        $total = [math]::Round($os.TotalVisibleMemorySize / 1MB, 1)
        Write-Host " [#] RAM: $free/$total GB free" -ForegroundColor Yellow
    } catch {}

    # Work dir
    Write-Host " [>] Work dir: $workDir" -ForegroundColor Blue

    # Last model
    if ($lastModel) {
        Write-Host " [+] Last used: $lastModel  (Press Enter to quick launch)" -ForegroundColor Cyan
    }

    Write-Host ""

    # Models
    $models = Get-Models
    Write-Host " Installed models:" -ForegroundColor White
    Write-Host ""

    for ($i = 0; $i -lt $models.Count; $i++) {
        $m = $models[$i]
        $num = $i + 1
        $display = $m.Name.PadRight(25)
        $tag = ""
        if ($m.Name -eq $running) { $tag = "  *RUNNING*" }
        if ($tag) {
            Write-Host "  $num. $display ($($m.Size))" -NoNewline -ForegroundColor Green
            Write-Host $tag -ForegroundColor Green
        } elseif ($m.Name -eq $lastModel) {
            Write-Host "  $num. $display ($($m.Size))" -ForegroundColor Cyan
        } else {
            Write-Host "  $num. $display ($($m.Size))"
        }
    }

    Write-Host ""
    Write-Host "  P. Pull (download) a new model" -ForegroundColor Magenta
    Write-Host "  D. Delete a model" -ForegroundColor Red
    Write-Host "  U. Update all models" -ForegroundColor Yellow
    Write-Host "  W. Change working directory" -ForegroundColor Blue
    Write-Host "  0. Exit" -ForegroundColor DarkGray
    Write-Host ""

    # Prompt
    $prompt = "  Select (0-$($models.Count)/P/D/U/W)"
    if ($lastModel) { $prompt += " [Enter=$lastModel]" }
    $prompt += ": "
    $choice = Read-Host $prompt

    # Quick launch
    if ([string]::IsNullOrEmpty($choice) -and $lastModel) {
        return @{ Action = "launch"; Model = $lastModel; Models = $models }
    }

    switch -Regex ($choice) {
        "^[Pp]$" { return @{ Action = "pull"; Models = $models } }
        "^[Dd]$" { return @{ Action = "delete"; Models = $models } }
        "^[Uu]$" { return @{ Action = "update"; Models = $models } }
        "^[Ww]$" { return @{ Action = "workdir"; Models = $models } }
        "^0$"    { return @{ Action = "exit" } }
        "^\d+$"  {
            $idx = [int]$choice - 1
            if ($idx -ge 0 -and $idx -lt $models.Count) {
                return @{ Action = "launch"; Model = $models[$idx].Name; Models = $models }
            }
            Write-Host "  Invalid choice." -ForegroundColor Red
            Start-Sleep -Seconds 1
            return @{ Action = "menu" }
        }
        default {
            Write-Host "  Invalid choice." -ForegroundColor Red
            Start-Sleep -Seconds 1
            return @{ Action = "menu" }
        }
    }
}

# Main loop
while ($true) {
    $result = Show-Menu

    switch ($result.Action) {
        "launch" {
            $script:lastModel = $result.Model
            Save-Config
            Write-Host ""
            Write-Host "  Launching $($result.Model) ..." -ForegroundColor Green
            Write-Host "  Working directory: $workDir" -ForegroundColor Blue
            Write-Host ""
            Set-Location $workDir
            ollama launch claude --model $result.Model
            Write-Host ""
            Read-Host "  Press Enter to continue"
        }
        "pull" {
            Write-Host ""
            $name = Read-Host "  Model name (e.g. phi3, mistral)"
            if ($name) {
                Write-Host "  Downloading $name ..." -ForegroundColor Yellow
                ollama pull $name
                Write-Host "  Done." -ForegroundColor Green
                Read-Host "  Press Enter to continue"
            }
        }
        "delete" {
            $models = $result.Models
            Write-Host ""
            $dc = Read-Host "  Select model to delete (1-$($models.Count))"
            $di = [int]$dc - 1
            if ($di -ge 0 -and $di -lt $models.Count) {
                $delName = $models[$di].Name
                $confirm = Read-Host "  Delete $delName? (Y/N)"
                if ($confirm -eq "Y" -or $confirm -eq "y") {
                    ollama rm $delName
                    Write-Host "  Deleted." -ForegroundColor Green
                    Read-Host "  Press Enter to continue"
                }
            }
        }
        "update" {
            $models = $result.Models
            for ($i = 0; $i -lt $models.Count; $i++) {
                $name = $models[$i].Name
                Write-Host "  [$($i+1)/$($models.Count)] Updating $name ..." -ForegroundColor Yellow
                ollama pull $name
            }
            Write-Host "  All models updated." -ForegroundColor Green
            Read-Host "  Press Enter to continue"
        }
        "workdir" {
            Write-Host ""
            $newDir = Read-Host "  New path"
            if ($newDir -and (Test-Path $newDir)) {
                $script:workDir = $newDir
                Save-Config
                Write-Host "  Changed to: $newDir" -ForegroundColor Green
            } else {
                Write-Host "  Directory not found." -ForegroundColor Red
            }
            Start-Sleep -Seconds 1
        }
        "exit" { exit }
    }
}
