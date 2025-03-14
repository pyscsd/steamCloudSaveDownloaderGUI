# Find signtool

$dir = dir "C:/Program Files (x86)/Windows Kits/10/bin/" | ?{$_.PSISContainer}

$newest_version = 0
$newest_version_path = ""
foreach ($d in $dir) {
    if (-Not ($d.EndsWith('.0'))) {
        Write-Host "Skip $($d)"
        continue
    }

    if (-Not (Test-Path "$($d)\x64\signtool.exe" -PathType Leaf)) {
        Write-Host "[no exe] Skip $($d)"
        continue
    }

    $leaf = $d.split("\")[-1]
    Write-Host "Leaf: $leaf"

    $version = $leaf -replace ".","" -as [int]

    if ($version -gt $newest_version) {
        $newest_version
        $newest_version_path = $d
    }
}

$signtool = "$($newest_version_path)\x64\signtool.exe"

Write-Host "Signtool: $($signtool)"

#certificate: '${{ secrets.SIGNTOOL_CERT }}'
#password: '${{ secrets.SIGNTOOL_PASS }}'
#certificatesha1: '${{ secrets.SIGNTOOL_FINGERPRINT }}'
#certificatename: '${{ secrets.SIGNTOOL_NAME }}'
#description: 'scsd-gui'
#timestampUrl: 'http://timestamp.digicert.com'
#folder: 'dist'
#recursive: true
