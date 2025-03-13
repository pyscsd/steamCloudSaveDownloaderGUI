# v1.2.3\n
$version_raw = Get-Content ./version.txt -Raw

$version = $version_raw -replace "`n",""  -replace "`r","" -replace "v",""
# 1.2.3

$first_ver, $second_ver, $third_ver = $version.split('.')

$version_template = Get-Content ./scripts/build/windows/version_template.txt -Raw

$version_template = $version_template -replace "ACHAKA1","($($first_ver), $($second_ver), $($third_ver), 0),"
$version_template = $version_template -replace "ACHAKA2","($($first_ver), $($second_ver), $($third_ver), 0),"
$version_template = $version_template -replace "ACHAKA3","v$($first_ver).$($second_ver).$($third_ver)"
$version_template = $version_template -replace "ACHAKA4","v$($first_ver).$($second_ver).$($third_ver)"
$version_template | Out-File -Filepath ./version_windows.txt -Encoding "UTF8"