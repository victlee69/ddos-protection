# PowerShell - DDoS Protection Installer
Write-Host "Installing on Windows..." -ForegroundColor Green
$dir = "$env:USERPROFILE\ddos_pro"
New-Item -ItemType Directory -Path $dir -Force | Out-Null
Set-Location $dir
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/victlee69/ddos-protection/main/setup_ddos_pro.py" -OutFile "setup.py"
python setup.py
Write-Host "Installation complete!" -ForegroundColor Yellow
