. .\scripts\build\windows\languages.ps1
foreach ($language in $languages)
{
    pyside6-lrelease.exe ".\steamCloudSaveDownloaderGUI\i18n\scsdGUI_$($language).ts" -qm ".\steamCloudSaveDownloaderGUI\res\scsdGUI_$($language).qm"
}
