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