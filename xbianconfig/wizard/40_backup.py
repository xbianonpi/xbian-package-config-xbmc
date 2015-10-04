import resources.lib.translation
_ = resources.lib.translation.language.gettext

DATA = {
    "title": _("Restore Home"),
    "smalltitle": _("Restore"),
    "description": _("XBian will offer you an easy way to backup your "
                     "setup.[CR]If you have a previous backup of your "
                     "home[CR](it contain your XBMC configuration, addons, "
                     "settings including Libraries...),[CR]"
                     "you can restore now.[CR][CR]"
                     "Later, if you want to do a backup, create a snapshot "
                     "and many more,[CR],go to system->xbian->backup"),
    "action": [
        'categories.55_backup.homeRestoreBackup',
    ],
}
