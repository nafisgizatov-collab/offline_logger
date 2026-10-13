function Test-SabyPython {
    param([Parameter(Mandatory=$true)][string]$FilePath, [string]$Prefix = '')
    # Windows app-execution aliases can open the Store instead of running Python.
    if ($FilePath -match '\\Microsoft\\WindowsApps\\') { return $null }
    $info = New-Object Diagnostics.ProcessStartInfo
    $info.FileName = $FilePath
    $info.Arguments = $Prefix + ' -c "import sys; print(''SABY_PYTHON_OK''); print(sys.executable); sys.exit(0 if sys.version_info >= (3,9) else 9)"'
    $info.UseShellExecute = $false
    $info.CreateNoWindow = $true
    $info.RedirectStandardOutput = $true
    $info.RedirectStandardError = $true
    $info.StandardOutputEncoding = [Text.Encoding]::UTF8
    $info.EnvironmentVariables['PYTHONIOENCODING'] = 'utf-8'
    $process = New-Object Diagnostics.Process
    $process.StartInfo = $info
    try {
        if (!$process.Start()) { return $null }
        $stdout = $process.StandardOutput.ReadToEndAsync()
        $stderr = $process.StandardError.ReadToEndAsync()
        if (!$process.WaitForExit(8000)) {
            try { $process.Kill() } catch {}
            return $null
        }
        $output = $stdout.Result.Trim() -split '\r?\n'
        if ($process.ExitCode -eq 0 -and $output.Count -eq 2 -and $output[0] -eq 'SABY_PYTHON_OK' -and (Test-Path -LiteralPath $output[1] -PathType Leaf)) { return $output[1] }
        return $null
    } catch { return $null }
    finally { $process.Dispose() }
}

function Resolve-SabyPython {
    $candidates = @()
    foreach ($name in @('py.exe', 'python.exe', 'python3.exe')) {
        foreach ($command in Get-Command $name -CommandType Application -All -ErrorAction SilentlyContinue) {
            $prefix = if ($name -eq 'py.exe') { '-3' } else { '' }
            $candidates += [pscustomobject]@{Path=$command.Source; Prefix=$prefix}
        }
    }
    $bundled = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
    $candidates += [pscustomobject]@{Path=$bundled; Prefix=''}
    foreach ($registry in @('HKCU:\Software\Python\PythonCore', 'HKLM:\Software\Python\PythonCore', 'HKLM:\Software\WOW6432Node\Python\PythonCore')) {
        foreach ($version in Get-ChildItem -LiteralPath $registry -ErrorAction SilentlyContinue) {
            $install = Get-Item -LiteralPath ($version.PSPath + '\InstallPath') -ErrorAction SilentlyContinue
            if ($install) {
                $exe = $install.GetValue('ExecutablePath')
                if (!$exe -and $install.GetValue('')) { $exe = Join-Path $install.GetValue('') 'python.exe' }
                if ($exe) { $candidates += [pscustomobject]@{Path=$exe; Prefix=''} }
            }
        }
    }
    $seen = @{}
    foreach ($candidate in $candidates) {
        $key = $candidate.Path + '|' + $candidate.Prefix
        if ($seen.ContainsKey($key)) { continue }
        $seen[$key] = $true
        if (!(Test-Path -LiteralPath $candidate.Path -PathType Leaf)) { continue }
        $python = Test-SabyPython -FilePath $candidate.Path -Prefix $candidate.Prefix
        if ($python) { return $python }
    }
    throw "Python 3.9 или новее не найден либо не запускается.`nУстановите Python для Windows: https://www.python.org/downloads/windows/`nПри установке включите Add python.exe to PATH. Затем повторите запуск установщика или отчета."
}
