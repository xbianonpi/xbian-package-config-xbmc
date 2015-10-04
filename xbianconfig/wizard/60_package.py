import resources.lib.translation
_ = resources.lib.translation.language.gettext

DATA = {
    "title": _("Install new packages"),
    "smalltitle": _("package"),
    "description": _("XBian comes with everything needed for XBMC but you can "
                     "easily add pre-configured  packages like Torrent, "
                     "Newsbin, CouchPotatoe and many more.[CR][CR]Users can "
                     "create their own package and share it with others. "
                     "If you feel you have something that others may like, "
                     "go to the XBian Forum and post a thread, and someone "
                     "will get back to you with information.[CR][CR]Please "
                     "be patient while the package list is loading."),
    "action": [
        'categories.30_packages.packagesManager',
    ],
}
