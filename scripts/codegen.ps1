# Ghi lai thao tac bang Playwright codegen. Chay tu thu muc goc project:
#   powershell -ExecutionPolicy Bypass -File scripts\codegen.ps1 tao_application
#   powershell -ExecutionPolicy Bypass -File scripts\codegen.ps1 ten_file -User truong.dangvan -Url "https://...#action=..."
# -User: tu dang nhap bang tai khoan nay (mat khau lay tu .env), codegen mo ra da login san.
# Code duoc luu vao codegen\<ten>.py
param(
    [string]$Name = "recording",
    [string]$User = "",
    [string]$Url = "https://vms-ta.stg.vti.com.vn/"
)
$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)

$py = ".\.venv\Scripts\python.exe"
$out = "codegen\$Name.py"
$cgArgs = @("-m", "playwright", "codegen", "--target", "python", "-o", $out)

if ($User) {
    Write-Host "Dang nhap ngam bang $User ..."
    & $py scripts\save_auth.py $User
    if ($LASTEXITCODE -ne 0) { throw "Dang nhap that bai: $User" }
    $cgArgs += "--load-storage=.auth\$User.json"
}

Write-Host "Dang mo codegen -> $out  (dong trinh duyet de luu)"
& $py @cgArgs $Url
Write-Host "Da luu: $out  - nho XOA MAT KHAU trong file truoc khi gui (neu co)."
