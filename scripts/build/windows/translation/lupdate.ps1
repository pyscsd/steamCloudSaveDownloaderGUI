. .\scripts\build\windows\translation\languages.ps1
foreach ($language in $languages)
{
    pyside6-lupdate.exe -extensions py -no-recursive .\steamCloudSaveDownloaderGUI -ts ".\steamCloudSaveDownloaderGUI\i18n\scsdGUI_$($language).ts"
}
