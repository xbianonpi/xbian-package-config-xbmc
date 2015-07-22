from resources.lib.xbianconfig import xbianConfig
import gettext
import xbmc

APP_NAME = "xbian"
LOCALE_DIR = '/usr/share/locale/'
 
DEFAULT_LANGUAGES = ['en']

languages = []

mo_location = LOCALE_DIR

gettext.textdomain (APP_NAME)
#gettext.bind_textdomain_codeset(APP_NAME, "UTF-8")
gettext.install(APP_NAME,mo_location,unicode=True)

try:
    xlanguage = xbmc.getLanguage(xbmc.ISO_639_1)
except:
    xlanguage = 'xbmc.getLanguage not supported'
    
print xlanguage

rc = gettext.find(APP_NAME, mo_location)
if rc:
    language = gettext.translation(APP_NAME, mo_location)
else:
    lc = xbianConfig('locales','select')[0].split('.')[0]
    if lc:
        languages = [lc]

    print lc

    languages += DEFAULT_LANGUAGES
    language = gettext.translation(APP_NAME, mo_location, languages=languages, fallback=True)


###print language.info()
