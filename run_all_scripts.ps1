# 宝可梦数据抓取自动化脚本
# Pokemon Data Scraper Automation Script
# Author: AI Assistant
# Version: 1.0

# 设置控制台编码为UTF-8
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# 颜色定义
$Colors = @{
    Red = "Red"
    Green = "Green"  
    Yellow = "Yellow"
    Blue = "Blue"
    Cyan = "Cyan"
    Magenta = "Magenta"
    White = "White"
}

# 脚本配置
$ScriptConfig = @{
    ScriptsPath = ".\scripts"
    LogFile = ".\pokemon_scraper_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
    MaxRetries = 3
    RetryDelay = 30
}

# 脚本执行顺序和配置
$Scripts = @(
    @{
        Name = "pokemon_list.py"
        Description = "抓取宝可梦基础列表"
        Required = $true
        EstimatedTime = 30
        Category = "基础数据"
    },
    @{
        Name = "ability_list.py"
        Description = "抓取特性列表"
        Required = $true
        EstimatedTime = 20
        Category = "基础数据"
    },
    @{
        Name = "move_list.py"
        Description = "抓取招式列表"
        Required = $true
        EstimatedTime = 25
        Category = "基础数据"
    },
    @{
        Name = "pokemon.py"
        Description = "抓取宝可梦详细信息"
        Required = $true
        EstimatedTime = 1800
        Category = "详细数据"
    },
    @{
        Name = "ability.py"
        Description = "抓取特性详细信息"
        Required = $true
        EstimatedTime = 600
        Category = "详细数据"
    },
    @{
        Name = "move.py"
        Description = "抓取招式详细信息"
        Required = $true
        EstimatedTime = 900
        Category = "详细数据"
    },
    @{
        Name = "pokemon_full_list.py"
        Description = "生成完整宝可梦列表"
        Required = $true
        EstimatedTime = 120
        Category = "汇总数据"
    },
    @{
        Name = "download_dream_image.py"
        Description = "下载宝可梦图片"
        Required = $false
        EstimatedTime = 900
        Category = "图片资源"
    }
)

# 日志函数
function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO",
        [string]$Color = "White"
    )
    
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogMessage = "[$Timestamp] [$Level] $Message"
    
    # 控制台输出（带颜色）
    Write-Host $LogMessage -ForegroundColor $Color
    
    # 文件日志
    Add-Content -Path $ScriptConfig.LogFile -Value $LogMessage -Encoding UTF8
}

function Write-Success {
    param([string]$Message)
    Write-Log "✅ $Message" -Level "SUCCESS" -Color $Colors.Green
}

function Write-Error {
    param([string]$Message)
    Write-Log "❌ $Message" -Level "ERROR" -Color $Colors.Red
}

function Write-Warning {
    param([string]$Message)
    Write-Log "⚠️  $Message" -Level "WARNING" -Color $Colors.Yellow
}

function Write-Info {
    param([string]$Message)
    Write-Log "ℹ️  $Message" -Level "INFO" -Color $Colors.Cyan
}

function Write-Header {
    param([string]$Title)
    
    $Border = "=" * 80
    Write-Host ""
    Write-Host $Border -ForegroundColor $Colors.Blue
    Write-Host $Title.PadLeft(($Border.Length + $Title.Length) / 2) -ForegroundColor $Colors.Blue
    Write-Host $Border -ForegroundColor $Colors.Blue
    Write-Host ""
}

function Format-Duration {
    param([int]$Seconds)
    
    if ($Seconds -lt 60) {
        return "${Seconds}秒"
    } elseif ($Seconds -lt 3600) {
        $Minutes = [math]::Floor($Seconds / 60)
        $Secs = $Seconds % 60
        return "${Minutes}分${Secs}秒"
    } else {
        $Hours = [math]::Floor($Seconds / 3600)
        $Minutes = [math]::Floor(($Seconds % 3600) / 60)
        return "${Hours}小时${Minutes}分钟"
    }
}

function Test-PythonEnvironment {
    Write-Info "检查Python环境..."
    
    try {
        $PythonVersion = python --version 2>&1
        if ($LASTEXITCODE -ne 0) {
            throw "Python未安装或不在PATH中"
        }
        Write-Success "Python环境检查通过: $PythonVersion"
        
        # 检查依赖包
        Write-Info "检查依赖包..."
        python -c "import requests, beautifulsoup4" 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "依赖包可能缺失，尝试安装..."
            pip install -r requirements.txt
        }
        
        return $true
    } catch {
        Write-Error "Python环境检查失败: $_"
        return $false
    }
}

function Start-ScriptExecution {
    param(
        [hashtable]$Script,
        [int]$Index,
        [int]$Total
    )
    
    $ScriptPath = Join-Path $ScriptConfig.ScriptsPath $Script.Name
    
    if (-not (Test-Path $ScriptPath)) {
        Write-Error "脚本文件不存在: $ScriptPath"
        return $false
    }
    
    Write-Info "[$($Index+1)/$Total] 开始执行: $($Script.Description)"
    Write-Info "预计用时: $(Format-Duration $Script.EstimatedTime)"
    Write-Info "脚本类型: $($Script.Category)"
    
    $StartTime = Get-Date
    $Success = $false
    $RetryCount = 0
    
    while ($RetryCount -lt $ScriptConfig.MaxRetries -and -not $Success) {
        if ($RetryCount -gt 0) {
            Write-Warning "第 $($RetryCount + 1) 次重试执行: $($Script.Name)"
            Start-Sleep -Seconds $ScriptConfig.RetryDelay
        }
        
        try {
            # 切换到脚本目录
            Push-Location $ScriptConfig.ScriptsPath
            
            # 执行Python脚本
            $Process = Start-Process -FilePath "python" -ArgumentList $Script.Name -Wait -PassThru -NoNewWindow -RedirectStandardOutput "temp_output.txt" -RedirectStandardError "temp_error.txt"
            
            # 显示输出
            if (Test-Path "temp_output.txt") {
                $Output = Get-Content "temp_output.txt" -Encoding UTF8
                if ($Output) {
                    $Output | ForEach-Object { Write-Host "  $_" -ForegroundColor $Colors.White }
                }
                Remove-Item "temp_output.txt" -ErrorAction SilentlyContinue
            }
            
            # 检查错误
            if (Test-Path "temp_error.txt") {
                $ErrorOutput = Get-Content "temp_error.txt" -Encoding UTF8
                if ($ErrorOutput) {
                    $ErrorOutput | ForEach-Object { Write-Host "  $_" -ForegroundColor $Colors.Red }
                }
                Remove-Item "temp_error.txt" -ErrorAction SilentlyContinue
            }
            
            Pop-Location
            
            if ($Process.ExitCode -eq 0) {
                $Success = $true
                $Duration = (Get-Date) - $StartTime
                Write-Success "$($Script.Description) 执行成功"
                Write-Info "实际用时: $(Format-Duration ([int]$Duration.TotalSeconds))"
            } else {
                throw "脚本执行失败，退出代码: $($Process.ExitCode)"
            }
            
        } catch {
            Pop-Location -ErrorAction SilentlyContinue
            $RetryCount++
            Write-Error "$($Script.Description) 执行失败: $_"
            
            if ($RetryCount -lt $ScriptConfig.MaxRetries) {
                Write-Warning "将在 $($ScriptConfig.RetryDelay) 秒后重试..."
            }
        }
    }
    
    if (-not $Success) {
        Write-Error "$($Script.Description) 执行失败，已达到最大重试次数"
    }
    
    Write-Host "-" * 60 -ForegroundColor $Colors.Blue
    return $Success
}

function Show-Summary {
    param(
        [array]$Results,
        [datetime]$StartTime
    )
    
    $TotalTime = (Get-Date) - $StartTime
    $SuccessCount = ($Results | Where-Object { $_ -eq $true }).Count
    $FailCount = ($Results | Where-Object { $_ -eq $false }).Count
    
    Write-Header "执行摘要"
    
    Write-Host "执行结果:" -ForegroundColor $Colors.Blue
    Write-Host "  成功: $SuccessCount" -ForegroundColor $Colors.Green
    Write-Host "  失败: $FailCount" -ForegroundColor $Colors.Red
    Write-Host "  总计: $($Results.Count)" -ForegroundColor $Colors.White
    Write-Host "  成功率: $([math]::Round($SuccessCount / $Results.Count * 100, 2))%" -ForegroundColor $Colors.Cyan
    Write-Host ""
    Write-Host "总执行时间: $(Format-Duration ([int]$TotalTime.TotalSeconds))" -ForegroundColor $Colors.Blue
    Write-Host "日志文件: $($ScriptConfig.LogFile)" -ForegroundColor $Colors.Blue
    
    if ($FailCount -gt 0) {
        Write-Warning "部分脚本执行失败，请检查日志文件获取详细信息"
    } else {
        Write-Success "所有脚本执行成功！"
    }
}

function Show-EstimatedTime {
    $TotalSeconds = ($Scripts | Measure-Object -Property EstimatedTime -Sum).Sum
    $RequiredSeconds = ($Scripts | Where-Object { $_.Required } | Measure-Object -Property EstimatedTime -Sum).Sum
    
    Write-Header "时间预估"
    Write-Host "必需脚本预计时间: $(Format-Duration $RequiredSeconds)" -ForegroundColor $Colors.Green
    Write-Host "全部脚本预计时间: $(Format-Duration $TotalSeconds)" -ForegroundColor $Colors.Yellow
    Write-Host ""
}

function Start-CompatibleMode {
    Write-Header "兼容模式执行"
    Write-Info "使用兼容性包装脚本执行所有任务"
    
    try {
        Push-Location $ScriptConfig.ScriptsPath
        
        $Process = Start-Process -FilePath "python" -ArgumentList "run_compatible.py" -Wait -PassThru -NoNewWindow
        
        Pop-Location
        
        if ($Process.ExitCode -eq 0) {
            Write-Success "兼容模式执行成功"
            return $true
        } else {
            Write-Error "兼容模式执行失败，退出代码: $($Process.ExitCode)"
            return $false
        }
    } catch {
        Pop-Location -ErrorAction SilentlyContinue
        Write-Error "兼容模式执行异常: $_"
        return $false
    }
}

function Main {
    Write-Header "宝可梦数据抓取自动化脚本"
    
    Write-Info "脚本版本: 1.0"
    Write-Info "执行时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    Write-Info "日志文件: $($ScriptConfig.LogFile)"
    Write-Host ""
    
    # 显示时间预估
    Show-EstimatedTime
    
    # 检查Python环境
    if (-not (Test-PythonEnvironment)) {
        Write-Error "Python环境检查失败，无法继续执行"
        return
    }
    
    # 询问执行模式
    Write-Host "选择执行模式:" -ForegroundColor $Colors.Yellow
    Write-Host "[1] 高级模式 - 使用新架构执行（推荐）" -ForegroundColor $Colors.Green
    Write-Host "[2] 兼容模式 - 使用现有脚本执行" -ForegroundColor $Colors.Blue
    Write-Host "[Q] 退出" -ForegroundColor $Colors.Red
    Write-Host "请选择：" -NoNewline -ForegroundColor $Colors.Yellow
    
    $ModeChoice = Read-Host
    
    switch ($ModeChoice.ToUpper()) {
        "2" { 
            $Success = Start-CompatibleMode
            if ($Success) {
                Write-Success "所有脚本执行完成！"
            } else {
                Write-Error "脚本执行失败"
            }
            return 
        }
        "Q" { 
            Write-Info "用户选择退出"
            return 
        }
        default { 
            Write-Info "选择高级模式"
        }
    }
    
    # 询问用户是否继续（高级模式）
    Write-Host "高级模式：是否继续执行所有脚本？包括图片下载可能需要很长时间。" -ForegroundColor $Colors.Yellow
    Write-Host "按 [Y] 继续全部执行，[N] 跳过图片下载，[Q] 退出：" -NoNewline -ForegroundColor $Colors.Yellow
    
    $Choice = Read-Host
    
    $SkipImages = $false
    switch ($Choice.ToUpper()) {
        "Q" { 
            Write-Info "用户选择退出"
            return 
        }
        "N" { 
            $SkipImages = $true
            Write-Info "将跳过图片下载"
        }
        default { 
            Write-Info "执行全部脚本"
        }
    }
    
    # 开始执行脚本
    $StartTime = Get-Date
    $Results = @()
    
    for ($i = 0; $i -lt $Scripts.Count; $i++) {
        $Script = $Scripts[$i]
        
        # 如果选择跳过图片下载
        if ($SkipImages -and $Script.Name -eq "download_dream_image.py") {
            Write-Warning "跳过图片下载脚本"
            continue
        }
        
        $Success = Start-ScriptExecution -Script $Script -Index $i -Total $Scripts.Count
        $Results += $Success
        
        # 如果是必需脚本失败，询问是否继续
        if (-not $Success -and $Script.Required) {
            Write-Host "必需脚本执行失败，是否继续执行？[Y/N]：" -NoNewline -ForegroundColor $Colors.Red
            $ContinueChoice = Read-Host
            if ($ContinueChoice.ToUpper() -ne "Y") {
                Write-Warning "用户选择停止执行"
                break
            }
        }
    }
    
    # 显示执行摘要
    Show-Summary -Results $Results -StartTime $StartTime
}

# 脚本入口点
try {
    Main
} catch {
    Write-Error "脚本执行过程中发生未处理的异常: $_"
} finally {
    Write-Host ""
    Write-Host "按任意键退出..." -ForegroundColor $Colors.Blue
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}
