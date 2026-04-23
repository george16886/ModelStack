# AI Model Launcher — PowerShell Version
# Lightweight alternative with colored output

$ErrorActionPreference = 'SilentlyContinue'
$ConfigFile = Join-Path $PSScriptRoot "config.txt"
$lastModel = ""
$workDir = $PWD.Path
$bookmarks = @()

# Load config
if (Test-Path $ConfigFile) {
    Get-Content $ConfigFile | ForEach-Object {
        if ($_ -match "^(.+?)=(.+)$") {
            switch ($Matches[1]) {
                "last_model" { $lastModel = $Matches[2] }
                "work_dir"   { $workDir = $Matches[2] }
                "bookmarks"  { $bookmarks = $Matches[2] -split '\|' | ForEach-Object { $_.Trim() } | Where-Object { $_ } }
            }
        }
    }
}

function Save-Config {
    $bmStr = $bookmarks -join '|'
    @("last_model=$lastModel", "work_dir=$workDir", "bookmarks=$bmStr") | Set-Content $ConfigFile
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
    Write-Host " ┌──────────────────────────────────────────────────────┐" -ForegroundColor Cyan
    Write-Host " │                 AI Model Launcher                    │" -ForegroundColor Cyan -NoNewline
    Write-Host "  (v2.0) " -ForegroundColor DarkGray
    Write-Host " └──────────────────────────────────────────────────────┘" -ForegroundColor Cyan
    Write-Host ""
    
    $running = Get-Running
    if ($running) {
        Write-Host "  ⦿ Running: " -NoNewline -ForegroundColor Green
        Write-Host $running -ForegroundColor White
    } else {
        Write-Host "  ⦿ Running: (none)" -ForegroundColor DarkGray
    }

    try {
        $gpu = nvidia-smi --query-gpu=memory.used,memory.total,utilization.gpu --format=csv,noheader,nounits 2>$null
        if ($gpu) {
            $p = $gpu -split ',\s*'
            Write-Host "  ⚛ GPU: " -NoNewline -ForegroundColor Yellow
            Write-Host "$($p[0])/$($p[1]) MB ($($p[2])%)"
        }
    } catch {}

    try {
        $os = Get-CimInstance Win32_OperatingSystem
        $free = [math]::Round($os.FreePhysicalMemory / 1MB, 1)
        $total = [math]::Round($os.TotalVisibleMemorySize / 1MB, 1)
        Write-Host "  ⚙ RAM: " -NoNewline -ForegroundColor Yellow
        Write-Host "$free/$total GB free"
    } catch {}

    Write-Host "  ➔ Dir: " -NoNewline -ForegroundColor Blue
    Write-Host $workDir
    
    if ($lastModel) {
        Write-Host "  ♥ Preferred: " -NoNewline -ForegroundColor Cyan
        Write-Host "$lastModel  (Enter to launch)"
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
    Write-Host "  B. Bookmarks" -ForegroundColor Cyan
    Write-Host "  T. Task Profiles" -ForegroundColor Yellow
    Write-Host "  X. Stop running model" -ForegroundColor Red
    Write-Host "  0. Exit" -ForegroundColor DarkGray
    Write-Host ""

    # Prompt
    $prompt = "  Select (0-$($models.Count)/P/D/U/W/B/X)"
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
        "^[Bb]$" { return @{ Action = "bookmarks" } }
        "^[Tt]$" { return @{ Action = "profiles" } }
        "^[Xx]$" { return @{ Action = "stop" } }
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
            Write-Host ""
            Write-Host "  Launching $($result.Model) ..." -ForegroundColor Green
            if (-not (Test-Path $workDir)) {
                Write-Host "  [!] Warning: Directory not found: $workDir" -ForegroundColor Yellow
                Write-Host "  [➔] Falling back to D:\" -ForegroundColor Cyan
                $workDir = "D:\"
            }
            Write-Host "  Working directory: $workDir" -ForegroundColor Blue
            Write-Host ""
            if (Test-Path $workDir) {
                Set-Location $workDir
            }
            ollama launch claude --model "$($result.Model)"
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
        "bookmarks" {
            Write-Host ""
            Write-Host "  Bookmarks:"
            for ($i = 0; $i -lt $bookmarks.Count; $i++) {
                Write-Host "  $($i+1). $($bookmarks[$i])"
            }
            Write-Host "  A. Add current directory"
            Write-Host "  D. Delete a bookmark"
            $bc = Read-Host "  Select bookmark (1-$($bookmarks.Count)/A/D)"
            if ($bc -eq "A" -or $bc -eq "a") {
                if ($bookmarks -notcontains $workDir) {
                    $script:bookmarks += $workDir
                    Save-Config
                    Write-Host "  Added." -ForegroundColor Green
                }
            } elseif ($bc -eq "D" -or $bc -eq "d") {
                $sel = Read-Host "  Index to delete"
                $di = [int]$sel - 1
                if ($di -ge 0 -and $di -lt $bookmarks.Count) {
                    $newBM = @()
                    for ($j=0; $j -lt $bookmarks.Count; $j++) {
                        if ($j -ne $di) { $newBM += $bookmarks[$j] }
                    }
                    $script:bookmarks = $newBM
                    Save-Config
                    Write-Host "  Removed." -ForegroundColor Green
                }
            } elseif ($bc -match '^\d+$') {
                $bi = [int]$bc - 1
                if ($bi -ge 0 -and $bi -lt $bookmarks.Count) {
                    $script:workDir = $bookmarks[$bi]
                    Save-Config
                    Write-Host "  Switched to: $workDir" -ForegroundColor Green
                }
            }
            Start-Sleep -Seconds 1
        }
        "stop" {
            $running = Get-Running
            if ($running) {
                $confirm = Read-Host "  Stop $running? (Y/N)"
                if ($confirm -eq "Y" -or $confirm -eq "y") {
                    ollama stop $running
                    Write-Host "  Stopped." -ForegroundColor Green
                    Read-Host "  Press Enter to continue"
                }
            } else {
                Write-Host "  No model is running." -ForegroundColor Red
                Start-Sleep -Seconds 1
            }
        }
        "profiles" {
            $profPath = Join-Path $PSScriptRoot "profiles.json"
            if (Test-Path $profPath) {
                try {
                    $json = Get-Content $profPath -Raw | ConvertFrom-Json
                    $profs = $json.profiles
                    Write-Host ""
                    Write-Host "  Task Profiles:" -ForegroundColor Yellow
                    for ($i = 0; $i -lt $profs.Count; $i++) {
                        $p = $profs[$i]
                        Write-Host "  $($i+1). $($p.name) ($($p.model))"
                    }
                    $pc = Read-Host "  Select profile (1-$($profs.Count))"
                    $pi = [int]$pc - 1
                    if ($pi -ge 0 -and $pi -lt $profs.Count) {
                        $p = $profs[$pi]
                        if ($p.model) { $script:lastModel = $p.model }
                        Save-Config
                        Write-Host "  Profile applied: $($p.name)" -ForegroundColor Green
                    }
                } catch {
                    Write-Host "  Error loading profiles." -ForegroundColor Red
                }
            } else {
                Write-Host "  profiles.json not found." -ForegroundColor Red
            }
            Start-Sleep -Seconds 1
        }
        "exit" { exit }
    }
}
