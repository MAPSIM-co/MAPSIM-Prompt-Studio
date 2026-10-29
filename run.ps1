<#
.SYNOPSIS
    MAPSIM Prompt Studio - one-command setup and launch for Windows.

.DESCRIPTION
    Finds a usable Python 3.10+, creates .venv in this folder, installs the pinned
    dependencies from requirements.txt (only when that file changes) and starts the
    local server. Nothing is interactive and nothing outside this project folder is
    touched. An existing .venv is never deleted: if it is broken the script stops and
    tells you what to do.

    An old `venv\` folder created by the previous version of run.bat is reused as-is,
    so upgrading does not install the dependencies twice.

.EXAMPLE
    run.bat
    Double-click, or run it from a terminal.

.EXAMPLE
    .\run.ps1 -Port 8005
    Start on another port.

.EXAMPLE
    .\run.ps1 -Tests
    Install dependencies and run the test suite, then exit.

.EXAMPLE
    .\run.ps1 -Reload -Open
    Development mode: restart on file changes and open the page once it answers.
#>
[CmdletBinding()]
param(
    [string] $BindHost = '',
    [int] $Port = 0,
    [string] $Python = '',
    [string] $VenvDir = '',
    [switch] $Reload,
    [switch] $Tests,
    [switch] $Open,
    [switch] $Help
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0

$MinMinor = 10
$ReqFile = 'requirements.txt'

function Write-Step { param([string] $Text) Write-Host ''; Write-Host "==> $Text" -ForegroundColor Cyan }
function Write-Say { param([string] $Text) Write-Host "    $Text" }
function Stop-With {
    param([string] $Text)
    Write-Host ''
    Write-Host "  x $Text" -ForegroundColor Red
    Write-Host ''
    exit 1
}

if ($Help) {
    Write-Host @'
Usage:  .\run.ps1 [-BindHost ADDRESS] [-Port NUMBER] [-Python PATH] [-VenvDir NAME]
                  [-Reload] [-Tests] [-Open] [-Help]

  -BindHost   bind address (default 127.0.0.1, or PROMPT_STUDIO_HOST)
  -Port       port number (default 8000, or PROMPT_STUDIO_PORT)
  -Python     interpreter to build the virtual environment with
  -VenvDir    folder for the virtual environment (default .venv, reuses venv if present)
  -Reload     restart the server when a source file changes
  -Tests      install dependencies and run the test suite, then exit
  -Open       open the app in the default browser once it is up
  -Help       show this help

The server reads the API key from PROMPT_STUDIO_API_KEY / GEMINI_API_KEY when the
variable is set, otherwise from config.json (or the Settings screen in the browser).
'@
    exit 0
}

Set-Location -LiteralPath $PSScriptRoot

if ([string]::IsNullOrWhiteSpace($BindHost)) { $BindHost = $env:PROMPT_STUDIO_HOST }
if ([string]::IsNullOrWhiteSpace($BindHost)) { $BindHost = '127.0.0.1' }
if ($Port -eq 0) {
    if ($env:PROMPT_STUDIO_PORT) { $Port = [int] $env:PROMPT_STUDIO_PORT } else { $Port = 8000 }
}
if ([string]::IsNullOrWhiteSpace($Python)) { $Python = $env:PROMPT_STUDIO_PYTHON }

if ($Port -lt 1 -or $Port -gt 65535) { Stop-With "-Port must be between 1 and 65535, got: $Port" }
if ($BindHost -notmatch '^[A-Za-z0-9._:\-]+$') { Stop-With "-BindHost contains unsupported characters: $BindHost" }
if (-not (Test-Path -LiteralPath $ReqFile -PathType Leaf)) {
    Stop-With "$ReqFile is missing - clone the whole repository, or run this script from inside it."
}

# --- find a usable interpreter -------------------------------------------------

function Test-Python {
    param([string] $Exe, [string[]] $PreArgs)
    $previousPreference = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        $probe = @('-c', "import sys; sys.exit(0 if sys.version_info[:2] >= (3, $MinMinor) else 1)")
        if ($PreArgs) { $probe = $PreArgs + $probe }
        $null = & $Exe @probe 2> $null
        return ($LASTEXITCODE -eq 0)
    } catch {
        return $false
    } finally {
        $ErrorActionPreference = $previousPreference
    }
}

function Get-PythonVersion {
    param([string] $Exe, [string[]] $PreArgs)
    $previousPreference = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        $probe = @('-c', 'import platform; print(platform.python_version())')
        if ($PreArgs) { $probe = $PreArgs + $probe }
        return ((& $Exe @probe 2> $null) | Select-Object -First 1)
    } catch {
        return 'unknown'
    } finally {
        $ErrorActionPreference = $previousPreference
    }
}

Write-Step "Checking for Python 3.$MinMinor or newer"

$candidates = @()
if (-not [string]::IsNullOrWhiteSpace($Python)) {
    $candidates += [pscustomobject] @{ Exe = $Python; PreArgs = $null; Label = $Python }
} else {
    foreach ($name in @('python3', 'python', 'py')) {
        $cmd = Get-Command $name -ErrorAction SilentlyContinue
        if ($cmd) {
            if ($name -eq 'py') { $candidates += [pscustomobject] @{ Exe = $cmd.Source; PreArgs = @('-3'); Label = 'py -3' } }
            else { $candidates += [pscustomobject] @{ Exe = $cmd.Source; PreArgs = $null; Label = $name } }
        }
    }
    $roots = @($env:LOCALAPPDATA, 'C:\', 'C:\Program Files', 'C:\Program Files (x86)')
    foreach ($root in $roots) {
        if ([string]::IsNullOrWhiteSpace($root)) { continue }
        foreach ($dir in @('Python3*', 'Programs\Python\Python3*')) {
            $pattern = Join-Path $root $dir
            Get-Item -Path $pattern -ErrorAction SilentlyContinue | ForEach-Object {
                $exe = Join-Path $_.FullName 'python.exe'
                if (Test-Path -LiteralPath $exe -PathType Leaf) {
                    $candidates += [pscustomobject] @{ Exe = $exe; PreArgs = $null; Label = $exe }
                }
            }
        }
    }
}

$chosen = $null
$chosenArgs = $null
$chosenLabel = ''
foreach ($cand in $candidates) {
    if (Test-Python -Exe $cand.Exe -PreArgs $cand.PreArgs) {
        $chosen = $cand.Exe
        $chosenArgs = $cand.PreArgs
        $chosenLabel = $cand.Label
        break
    }
}
if (-not $chosen) {
    if (-not [string]::IsNullOrWhiteSpace($Python)) {
        Stop-With "'$Python' is not a usable Python 3.$MinMinor+ interpreter (check the path and the version)."
    }
    Write-Host "    No usable Python interpreter was found. Install one, then run this script again:" -ForegroundColor Yellow
    Write-Host "      winget install Python.Python.3.12" -ForegroundColor Yellow
    Write-Host "      https://www.python.org/downloads/windows/  (tick 'Add python.exe to PATH')" -ForegroundColor Yellow
    Stop-With "Python 3.$MinMinor or newer is required."
}
Write-Say "using: $chosenLabel ($(Get-PythonVersion -Exe $chosen -PreArgs $chosenArgs))"

# --- virtual environment ------------------------------------------------------

Write-Step 'Preparing the virtual environment'

if ([string]::IsNullOrWhiteSpace($VenvDir)) {
    if (Test-Path -LiteralPath 'venv\Scripts\python.exe' -PathType Leaf) {
        $VenvDir = 'venv'
    } else {
        $VenvDir = '.venv'
    }
}
$venvPy = Join-Path (Join-Path $VenvDir 'Scripts') 'python.exe'

if ((Test-Path -LiteralPath $VenvDir -PathType Container) -and -not (Test-Path -LiteralPath $venvPy -PathType Leaf)) {
    Stop-With "$VenvDir exists but has no working interpreter inside it. Rename the folder (ren $VenvDir ${VenvDir}.broken) and run this script again, or point it at an interpreter with -Python C:\path\to\python.exe."
}
if (-not (Test-Path -LiteralPath $venvPy -PathType Leaf)) {
    $createArgs = @('-m', 'venv', $VenvDir)
    if ($chosenArgs) { $createArgs = $chosenArgs + $createArgs }
    & $chosen @createArgs
    if ($LASTEXITCODE -ne 0) { Stop-With "Could not create the virtual environment in $VenvDir." }
}
if (-not (Test-Path -LiteralPath $venvPy -PathType Leaf)) { Stop-With "The virtual environment was created but $venvPy is missing." }

# --- dependencies -------------------------------------------------------------

Write-Step 'Installing pinned dependencies'

$hashFile = Join-Path $VenvDir '.requirements.sha256'
$current = (Get-FileHash -Algorithm SHA256 -LiteralPath $ReqFile).Hash.ToLowerInvariant()
$previous = ''
if (Test-Path -LiteralPath $hashFile -PathType Leaf) { $previous = (Get-Content -LiteralPath $hashFile -Raw).Trim().ToLowerInvariant() }

if ($current -ne $previous) {
    & $venvPy -m pip install --upgrade pip --quiet --disable-pip-version-check
    if ($LASTEXITCODE -ne 0) { Stop-With 'pip could not be upgraded. Check your network connection, then run this script again.' }
    & $venvPy -m pip install -r $ReqFile --disable-pip-version-check
    if ($LASTEXITCODE -ne 0) { Stop-With 'Dependency installation failed. This step needs internet access the first time you run the script.' }
    Set-Content -LiteralPath $hashFile -Value $current -Encoding ascii -NoNewline
} else {
    Write-Say 'already satisfied (requirements.txt unchanged)'
}

if ($Tests) {
    Write-Step 'Running the test suite'
    & $venvPy -m unittest discover -s tests -v
    exit $LASTEXITCODE
}

# --- port, warnings, launch ---------------------------------------------------

Write-Step "Checking that port $Port is free on $BindHost"

$address = [System.Net.IPAddress]::Any
if ([System.Net.IPAddress]::TryParse($BindHost, [ref] $address)) {
    $listener = New-Object System.Net.Sockets.TcpListener($address, $Port)
    try {
        $listener.Start()
        $listener.Stop()
    } catch {
        try { $listener.Stop() } catch { }
        Write-Host "    Something is already listening on ${BindHost}:$Port - usually an older instance of this app." -ForegroundColor Yellow
        Write-Host '    Stop it, or choose another port:  .\run.ps1 -Port 8005' -ForegroundColor Yellow
        Stop-With "Port $Port is busy."
    }
} else {
    Write-Say "skipped (cannot resolve '$BindHost' to an IP address; uvicorn will report any conflict)"
}

if ($BindHost -ne '127.0.0.1' -and $BindHost -ne 'localhost') {
    Write-Host ''
    Write-Host "  WARNING: binding to $BindHost lets other machines on this network use" -ForegroundColor Yellow
    Write-Host '  your Gemini API key through this page. Only do that on a network you trust.' -ForegroundColor Yellow
}

if ([string]::IsNullOrWhiteSpace($env:PROMPT_STUDIO_API_KEY) -and [string]::IsNullOrWhiteSpace($env:GEMINI_API_KEY) -and -not (Test-Path -LiteralPath 'config.json' -PathType Leaf)) {
    Write-Host ''
    Write-Host '  No API key configured yet: open the page, press the Settings button and paste' -ForegroundColor Yellow
    Write-Host '  a Google AI Studio key (https://aistudio.google.com/apikey). It is stored in' -ForegroundColor Yellow
    Write-Host '  config.json and never sent back to the browser.' -ForegroundColor Yellow
}

$url = "http://$BindHost:$Port"
$serverArgs = @('-m', 'uvicorn', 'prompt_compiler.app:app', '--host', $BindHost, '--port', "$Port")
if ($Reload) { $serverArgs += '--reload' }

Write-Step 'Starting MAPSIM Prompt Studio'
Write-Say "$url   (press Ctrl+C to stop)"
if ($Open) {
    # A job, not Start-Process: opening the browser immediately would land on a
    # page that has not bound its port yet. The job polls loopback until the app
    # answers (max 10 seconds) and only then hands the URL to the browser.
    Start-Job -ArgumentList $url -ScriptBlock {
        param($Target)
        for ($attempt = 0; $attempt -lt 20; $attempt++) {
            try {
                Invoke-WebRequest -Uri $Target -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop | Out-Null
                break
            } catch {
                Start-Sleep -Milliseconds 500
            }
        }
        Start-Process $Target
    } | Out-Null
}

& $venvPy @serverArgs
exit $LASTEXITCODE
