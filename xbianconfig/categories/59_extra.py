from resources.lib.xbmcguie.category import Category
import categories.extra as extrasetting

import resources.lib.translation
_ = resources.lib.translation.language.ugettext


class extra(Category):
    SETTINGS = extrasetting.extra()
    if SETTINGS:
        TITLE = _('extra')
    else:
        TITLE = None
