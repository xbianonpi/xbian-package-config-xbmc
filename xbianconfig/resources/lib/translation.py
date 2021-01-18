import gettext
import locale

import xbmc

from resources.lib.xbianconfig import xbianConfig


APP_NAME = "xbian-config"
CODESET = "UTF-8"


gettext.bindtextdomain(APP_NAME)
gettext.textdomain(APP_NAME)
gettext.bind_textdomain_codeset(APP_NAME, CODESET)
gettext.install(APP_NAME)

try:
    xbmc_lang = xbmc.getLanguage(xbmc.ISO_639_1)
except Exception:
    xbmc_lang = None

xbian_lang = xbianConfig('locales', 'select')[0].split('.')[0]
system_lang = locale.getlocale(locale.LC_MESSAGES)[0]
if not system_lang:
    system_lang = locale.getdefaultlocale()[0]

# The priority is: xbmc => xbian => system
languages = [
    lang for lang in [xbmc_lang, xbian_lang, system_lang] if lang]
language = gettext.translation(
    APP_NAME, languages=languages, fallback=True, codeset=CODESET)
