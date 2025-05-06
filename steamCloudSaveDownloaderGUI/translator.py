from PySide6.QtCore import QLocale, QLibraryInfo, QObject, QTranslator
from PySide6 import QtWidgets as QW
from . import data_provider
from .steamCloudSaveDownloader.steamCloudSaveDownloader.logger import logger
from .res import translations

def reload_translator():
    path = QLibraryInfo.location(QLibraryInfo.LibraryPath.TranslationsPath)

    app = QW.QApplication.instance()
    translator = QTranslator(app)

    language_code = data_provider.config['GUI']['language']
    if language_code == 'system':
        locale = QLocale.system()
    else:
        locale = QLocale(language_code)
    logger.debug(f"Translation set to: {language_code}")

    if translator.load(locale, 'qtbase', '_', path):
        app.installTranslator(translator)
    translator = QTranslator(app)
    path = ":/translations"
    if translator.load(locale, 'scsdGUI', '_', path):
        app.installTranslator(translator)