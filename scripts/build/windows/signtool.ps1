param (
    #'${{ secrets.SIGNTOOL_CERT }}'
    [Parameter(Mandatory=$true)]
    [String]$cert_base64,

    #'${{ secrets.SIGNTOOL_PASS }}'
    [Parameter(Mandatory=$true)]
    [String]$cert_passwd,

    #'${{ secrets.SIGNTOOL_FINGERPRINT }}'
    [Parameter(Mandatory=$true)]
    [String]$cert_fingerprint,

    #'${{ secrets.SIGNTOOL_NAME }}'
    [Parameter(Mandatory=$true)]
    [String]$cert_name,

    [Parameter(Mandatory=$true)]
    [String]$target
)

# Find signtool

$dir = Get-ChildItem "C:/Program Files (x86)/Windows Kits/10/bin/" | Where-Object{$_.PSISContainer}

$newest_version = 0
$newest_version_path = ""
foreach ($d in $dir) {
    if (-Not ($d.FullName.EndsWith('.0'))) {
        Write-Host "Skip $($d)"
        continue
    }

    if (-Not (Test-Path "$($d.FullName)\x64\signtool.exe" -PathType Leaf)) {
        Write-Host "[no exe] Skip $($d)"
        continue
    }

    $leaf = $d.FullName.split("\")[-1]

    $version = ($leaf -replace "\.","") -as [int]
    Write-Host "Leaf: $($leaf) Version: $($version)"

    if ($version -gt $newest_version) {
        $newest_version = $version
        $newest_version_path = $d.FullName
    }
}

$signtool = "$($newest_version_path)\x64\signtool.exe"

Write-Host "Signtool: $($signtool)"

$certificate = '.\certificate.pfx'

# Create Cert
$cert_bytes = [Convert]::FromBase64String($cert_base64)
[IO.File]::WriteAllBytes($certificate, $cert_bytes)

# Import Cert
certutil -f -p $cert_passwd -importpfx $certificate
Set-Location Cert:\CurrentUser\My

# Sign
$command = "$($signtool) sign /f $($certificate) /p $($cert_passwd) /fd SHA256 /tr http://timestamp.digicert.com /td SHA256 $($target)"
Invoke-Command $command