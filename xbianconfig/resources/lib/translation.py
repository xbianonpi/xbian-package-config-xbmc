import gettext
import os

import xbmc

from resources.lib.xbianconfig import xbianConfig


APP_NAME = "xbian"
LOCALE_DIR = os.path.join([
    os.path.dirname(os.path.abspath(__file__)),
    os.path.pardir, os.path.pardir, 'po'])

gettext.textdomain(APP_NAME)
# gettext.bind_textdomain_codeset(APP_NAME, "UTF-8")
gettext.install(APP_NAME, LOCALE_DIR, unicode=True)

try:
    xlanguage = xbmc.getLanguage(xbmc.ISO_639_1)
except Exception:
    xlanguage = 'xbmc.getLanguage not supported'

rc = gettext.find(APP_NAME, LOCALE_DIR)
if rc:
    language = gettext.translation(APP_NAME, LOCALE_DIR)
else:
    lc = xbianConfig('locales', 'select')[0].split('.')[0]
    languages = []
    if lc:
        languages = [lc]

    language = gettext.translation(
        APP_NAME, LOCALE_DIR, languages=languages, fallback=True)
