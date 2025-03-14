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
    Write-Host "Leaf: $leaf"

    $version = $leaf -replace ".","" -as [int]

    if ($version -gt $newest_version) {
        $newest_version
        $newest_version_path = $d
    }
}

$signtool = "$($newest_version_path)\x64\signtool.exe"

Write-Host "Signtool: $($signtool)"

