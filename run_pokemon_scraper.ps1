# Pokemon Data Scraper - Simplified Version
# Author: AI Assistant
# Version: 1.0

# Set UTF-8 encoding for output
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Script configuration
$ScriptsPath = ".\scripts"
$LogFile = ".\pokemon_scraper_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"

# Script execution order
$Scripts = @(
    @{ Name = "pokemon_list.py"; Description = "Pokemon List"; Time = 30 },
    @{ Name = "ability_list.py"; Description = "Ability List"; Time = 20 },
    @{ Name = "move_list.py"; Description = "Move List"; Time = 25 },
    @{ Name = "pokemon.py"; Description = "Pokemon Details"; Time = 1800 },
    @{ Name = "ability.py"; Description = "Ability Details"; Time = 600 },
    @{ Name = "move.py"; Description = "Move Details"; Time = 900 },
    @{ Name = "pokemon_full_list.py"; Description = "Full Pokemon List"; Time = 120 },
    @{ Name = "download_dream_image.py"; Description = "Download Images"; Time = 900 }
)

# Log function
function Write-Log {
    param([string]$Message, [string]$Color = "White")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogMessage = "[$Timestamp] $Message"
    Write-Host $LogMessage -ForegroundColor $Color
    Add-Content -Path $LogFile -Value $LogMessage -Encoding UTF8
}

function Write-Header {
    param([string]$Title)
    Write-Host ""
    Write-Host "=" * 60 -ForegroundColor Blue
    Write-Host $Title -ForegroundColor Blue
    Write-Host "=" * 60 -ForegroundColor Blue
    Write-Host ""
}

function Format-Time {
    param([int]$Seconds)
    if ($Seconds -lt 60) { return "${Seconds}s" }
    elseif ($Seconds -lt 3600) { 
        $m = [math]::Floor($Seconds / 60)
        $s = $Seconds % 60
        return "${m}m${s}s"
    } else {
        $h = [math]::Floor($Seconds / 3600)
        $m = [math]::Floor(($Seconds % 3600) / 60)
        return "${h}h${m}m"
    }
}

function Test-Environment {
    Write-Log "Checking Python environment..." "Cyan"
    try {
        $version = python --version 2>&1
        if ($LASTEXITCODE -ne 0) {
            throw "Python not found"
        }
        Write-Log "Python check passed: $version" "Green"
        return $true
    } catch {
        Write-Log "Python environment check failed: $_" "Red"
        return $false
    }
}

function Run-Script {
    param([hashtable]$Script, [int]$Index, [int]$Total)
    
    $ScriptPath = Join-Path $ScriptsPath $Script.Name
    if (-not (Test-Path $ScriptPath)) {
        Write-Log "Script not found: $ScriptPath" "Red"
        return $false
    }
    
    Write-Log "[$($Index+1)/$Total] Starting: $($Script.Description)" "Yellow"
    Write-Log "Estimated time: $(Format-Time $Script.Time)" "Cyan"
    
    $StartTime = Get-Date
    
    try {
        Push-Location $ScriptsPath
        $Process = Start-Process -FilePath "python" -ArgumentList $Script.Name -Wait -PassThru -NoNewWindow
        Pop-Location
        
        if ($Process.ExitCode -eq 0) {
            $Duration = (Get-Date) - $StartTime
            Write-Log "$($Script.Description) completed successfully" "Green"
            Write-Log "Actual time: $(Format-Time ([int]$Duration.TotalSeconds))" "Cyan"
            return $true
        } else {
            Write-Log "$($Script.Description) failed with exit code: $($Process.ExitCode)" "Red"
            return $false
        }
    } catch {
        Pop-Location -ErrorAction SilentlyContinue
        Write-Log "$($Script.Description) failed with exception: $_" "Red"
        return $false
    } finally {
        Write-Host "-" * 60 -ForegroundColor Blue
    }
}

function Main {
    Write-Header "Pokemon Data Scraper"
    
    Write-Log "Script Version: 1.0" "Cyan"
    Write-Log "Start Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" "Cyan"
    Write-Log "Log File: $LogFile" "Cyan"
    
    # Show estimated time
    $TotalTime = ($Scripts | Measure-Object -Property Time -Sum).Sum
    Write-Log "Estimated total time: $(Format-Time $TotalTime)" "Yellow"
    
    # Check environment
    if (-not (Test-Environment)) {
        Write-Log "Environment check failed, cannot continue" "Red"
        return
    }
    
    # Ask user
    Write-Host "Continue with all scripts? Images download may take long time." -ForegroundColor Yellow
    Write-Host "[Y] Continue all, [N] Skip images, [Q] Quit: " -NoNewline -ForegroundColor Yellow
    $Choice = Read-Host
    
    $SkipImages = $false
    switch ($Choice.ToUpper()) {
        "Q" { 
            Write-Log "User chose to quit"
            return 
        }
        "N" { 
            $SkipImages = $true
            Write-Log "Will skip image download"
        }
        default { 
            Write-Log "Executing all scripts"
        }
    }
    
    # Execute scripts
    $StartTime = Get-Date
    $Results = @()
    
    for ($i = 0; $i -lt $Scripts.Count; $i++) {
        $Script = $Scripts[$i]
        
        # Skip images if requested
        if ($SkipImages -and $Script.Name -eq "download_dream_image.py") {
            Write-Log "Skipping image download script" "Yellow"
            continue
        }
        
        $Success = Run-Script -Script $Script -Index $i -Total $Scripts.Count
        $Results += $Success
        
        # Ask to continue on failure
        if (-not $Success) {
            Write-Host "Script failed. Continue? [Y/N]: " -NoNewline -ForegroundColor Red
            $Continue = Read-Host
            if ($Continue.ToUpper() -ne "Y") {
                Write-Log "User chose to stop execution" "Yellow"
                break
            }
        }
    }
    
    # Show summary
    $EndTime = Get-Date
    $TotalDuration = $EndTime - $StartTime
    $SuccessCount = ($Results | Where-Object { $_ -eq $true }).Count
    $TotalCount = $Results.Count
    
    Write-Header "Execution Summary"
    Write-Log "Total Scripts: $TotalCount" "Cyan"
    Write-Log "Successful: $SuccessCount" "Green"
    Write-Log "Failed: $($TotalCount - $SuccessCount)" "Red"
    Write-Log "Success Rate: $([math]::Round($SuccessCount / $TotalCount * 100, 2))%" "Cyan"
    Write-Log "Total Duration: $(Format-Time ([int]$TotalDuration.TotalSeconds))" "Cyan"
    
    if ($SuccessCount -eq $TotalCount) {
        Write-Log "All scripts completed successfully!" "Green"
    } else {
        Write-Log "Some scripts failed. Check log for details." "Yellow"
    }
}

# Entry point
try {
    Main
} catch {
    Write-Log "Unhandled exception: $_" "Red"
} finally {
    Write-Host ""
    Write-Host "Press any key to exit..." -ForegroundColor Blue
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

