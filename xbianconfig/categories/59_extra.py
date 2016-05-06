from resources.lib.xbmcguie.category import Category
import categories.extra as extrasetting

import resources.lib.translation
_ = resources.lib.translation.language.gettext


class extra(Category):
    SETTINGS = extrasetting.extra()
    if SETTINGS:
        TITLE = _('Extra')
    else:
        TITLE = None
