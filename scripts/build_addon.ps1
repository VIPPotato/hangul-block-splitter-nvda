param(
	[string]$OutputDir = "dist",
	[string]$Version,
	[switch]$Dev,
	[string]$Channel
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$pythonCmd = Get-Command py -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
	throw "Python launcher 'py' was not found. Install Python (with py launcher) first."
}

Push-Location $repoRoot
try {
	$sconsArgs = @("-Q")
	if ($Version) {
		$sconsArgs += "version=$Version"
	}
	if ($Dev.IsPresent) {
		$sconsArgs += "dev=1"
	}
	if ($Channel) {
		$sconsArgs += "channel=$Channel"
	}

	& py -3 -m SCons @sconsArgs
	if ($LASTEXITCODE -ne 0) {
		throw "SCons build failed with exit code $LASTEXITCODE"
	}

	$builtAddon = Get-ChildItem -LiteralPath $repoRoot -Filter "*.nvda-addon" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
	if (-not $builtAddon) {
		throw "No .nvda-addon artifact was produced by SCons."
	}

	$outputPath = Join-Path $repoRoot $OutputDir
	New-Item -ItemType Directory -Force -Path $outputPath | Out-Null
	$finalPath = Join-Path $outputPath $builtAddon.Name
	Move-Item -LiteralPath $builtAddon.FullName -Destination $finalPath -Force

	Write-Output "Built add-on package: $finalPath"
}
finally {
	Pop-Location
}
