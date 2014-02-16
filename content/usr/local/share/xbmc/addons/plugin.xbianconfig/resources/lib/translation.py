import os
from resources.lib.xbianconfig import xbianConfig
import gettext

APP_NAME = "xbian"
LOCALE_DIR = '/usr/share/locale/'
 
DEFAULT_LANGUAGES = ['en']

languages = []

lc = xbianConfig('locales','select')[0].split('.')[0]
lc = 'nl_NL'
if lc:
    languages = [lc]
print lc

languages += DEFAULT_LANGUAGES
mo_location = LOCALE_DIR

print languages 

gettext.find(APP_NAME, mo_location)
gettext.textdomain (APP_NAME)
#gettext.bind_textdomain_codeset(APP_NAME, "UTF-8")
gettext.install(APP_NAME,mo_location,unicode=True)

language = gettext.translation(APP_NAME, mo_location, languages=languages, fallback=True)


