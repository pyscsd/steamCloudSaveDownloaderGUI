import sys
import os

__version__ = None

def meipass_ver():
    if not hasattr(sys, '_MEIPASS'):
        return None
    ver_file = os.path.join(sys._MEIPASS, 'version.txt')
    if not os.path.isfile(ver_file):
        return None
    with open(ver_file) as f:
        return f.readline().strip()

__version__ = meipass_ver()

if __version__ is None:
    __version__ = "Version Unknown"
