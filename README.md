<p align="center">
<img src="./steamCloudSaveDownloaderGUI/res/scsd_icon.jpg" width="128">
</p>

steamCloudSaveDownloaderGUI
===========
[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE) [![Check/Build](https://github.com/pyscsd/steamCloudSaveDownloaderGUI/actions/workflows/check-test-build.yml/badge.svg)](https://github.com/pyscsd/steamCloudSaveDownloaderGUI/actions/workflows/check-test-build.yml/) [![Publish](https://github.com/pyscsd/steamCloudSaveDownloaderGUI/actions/workflows/publish.yml/badge.svg)](https://github.com/pyscsd/steamCloudSaveDownloaderGUI/actions/workflows/publish.yml/) [![GitHub Release](https://img.shields.io/github/v/release/pyscsd/steamCloudSaveDownloaderGUI)](https://github.com/pyscsd/steamCloudSaveDownloaderGUI/releases)


Download and backup saves from Steam Cloud automatically. A must-have tool for every PC gamer.

This is an official frontend implementation to [scsd](https://github.com/pyscsd/steamCloudSaveDownloader) in Python/Qt

> [!WARNING]
> This program is in alpha stage. Expect bugs and breaking changes. Use at your own risk.

#### [📄Documentation](https://github.com/pyscsd/steamCloudSaveDownloaderGUI/wiki) | [⏬Download](https://github.com/pyscsd/steamCloudSaveDownloaderGUI/releases)

## :warning: DISCLAIMER
- This program is not affiliated with Valve or Steam. Steam is a trademark of Valve Corporation.
- This program does not come with warranty and use at your own risk. Even though this program is thoroughly tested and theoretically does not violate EULA.

## Descriptions
For supported games, Steam will automatically upload game saves to the cloud. This is intended for seamless playing across multiple devices, but NOT as a form of backup. Assume your game save is corrupted by the game itself, or you accidently did something that cannot be undone. Steam will automatically uploads the newest(corrupted) game saves to the cloud once you close the game. This is when this tool come to the rescue.

This program automatically crawls the [Steam cloud webpages](https://store.steampowered.com/account/remotestorage) and download the files. A number of copies are kept locally in case something goes wrong. You can rollback your saves whenever anything goes wrong.

## Screenshots
<p float="left">
    <img src="./docs/screenshots/main_window.png" width="48%" />
    <img src="./docs/screenshots/file_dialog.png" width="48%" />
</p>

## Features
- Easy to setup (in less than one minute)
- Secure
- Periodically download in background
- Intuitive interface
- More to come...

## How to build
```
pip install -r requirements-dev.txt
python3 scsd-gui
```

## Special Thanks
- Alpha Test: Kadachy@@@, maer