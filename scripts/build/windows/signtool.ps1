# Find signtool

$dir = dir "C:/Program Files (x86)/Windows Kits/10/bin/" | ?{$_.PSISContainer}

foreach ($d in $dir) {
    Write-Host $d
    Write-Host $d.FullName
    #if (-Not ($d.FullName.EndsWith('.0'))) {
    #    Write-Host "  continue"
    #    continue
    #}

    #$version =
}

#certificate: '${{ secrets.SIGNTOOL_CERT }}'
#password: '${{ secrets.SIGNTOOL_PASS }}'
#certificatesha1: '${{ secrets.SIGNTOOL_FINGERPRINT }}'
#certificatename: '${{ secrets.SIGNTOOL_NAME }}'
#description: 'scsd-gui'
#timestampUrl: 'http://timestamp.digicert.com'
#folder: 'dist'
#recursive: true
