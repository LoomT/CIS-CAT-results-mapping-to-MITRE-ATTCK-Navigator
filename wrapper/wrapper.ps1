<#  Assessor-CLI PowerShell wrapper
    Adds -json, then uploads latest reports\*.json
#>

param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$RemainingArgs
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition

# 1. Find the .bat file to run
if ($RemainingArgs.Count -gt 0 -and
    $RemainingArgs[0] -match '\.bat$' -and
    (Test-Path $RemainingArgs[0])) {

    $cliPath = (Resolve-Path $RemainingArgs[0]).Path
    $RemainingArgs = $RemainingArgs[1..($RemainingArgs.Count-1)]
}
else {
    $cliPath = Join-Path $scriptDir 'Assessor-CLI.bat'
}

if (-not (Test-Path $cliPath)) {
    Write-Error "CLI not found: $cliPath"
    exit 1
}

# 2. load env vars from .wrapper.env
$envFile = Join-Path $scriptDir '.wrapper.env'
if (-not (Test-Path $envFile)) {
    Write-Error ".wrapper.env not found"
    exit 1
}

Get-Content $envFile | ForEach-Object {
    if ($_ -match '^\s*([^#=]+)=([^#]+)') {
        Set-Variable -Name $Matches[1].Trim() -Value $Matches[2].Trim() -Scope Script
    }
}
if (-not $POST_URL -or -not $POST_BEARER) {
    Write-Error "POST_URL / POST_BEARER missing in env file"
    exit 1
}

# Take a snapshot of the last .json file
$reportDir = Join-Path (Split-Path $cliPath -Parent) 'reports'
$preLatest = Get-ChildItem -Path $reportDir -Filter *.json -ErrorAction SilentlyContinue |
             Sort-Object -Property LastWriteTime -Descending |
             Select-Object -First 1

# 3. run the CLI with -json added
& $cliPath -json @RemainingArgs

# 4. pick newest JSON report
$reportDir = Join-Path (Split-Path $cliPath -Parent) 'reports'
$latest = Get-ChildItem -Path $reportDir -Filter *.json |
          Sort-Object -Property LastWriteTime -Descending |
          Select-Object -First 1
if (-not $latest) {
    Write-Error "No JSON reports in $reportDir"
    exit 1
}

if ($preLatest -and ($latest.FullName -eq $preLatest.FullName)) {
    Write-Error "No new JSON report generated. Aborting upload."
    exit 1
}

# 5. upload multipart/form-data
try {
    # Works on PowerShell 7+
    Invoke-RestMethod -Uri $POST_URL `
        -Headers @{ Authorization = "Bearer $POST_BEARER" } `
        -Method Post -Form @{ file = Get-Item $latest.FullName }
}
catch [System.Management.Automation.ParameterBindingException] {
    # Fallback for Windows PowerShell 5.x
    Add-Type -AssemblyName System.Net.Http

    $client = New-Object System.Net.Http.HttpClient
    $boundary = [System.Guid]::NewGuid().ToString()
    $content = New-Object System.Net.Http.MultipartFormDataContent $boundary

    $bytes = [IO.File]::ReadAllBytes($latest.FullName)
    $filePart = [System.Net.Http.ByteArrayContent]::new($bytes)
    $filePart.Headers.ContentType =
        [System.Net.Http.Headers.MediaTypeHeaderValue]::Parse('application/json')
    $content.Add($filePart, 'file', $latest.Name)

    $client.DefaultRequestHeaders.Authorization =
        New-Object System.Net.Http.Headers.AuthenticationHeaderValue('Bearer', $POST_BEARER)

    $response  = $client.PostAsync($POST_URL, $content).Result
    $response.EnsureSuccessStatusCode() | Out-Null
    $response.Content.ReadAsStringAsync().Result
}
catch {
    Write-Error "Upload failed: $_"
    exit 1
}
