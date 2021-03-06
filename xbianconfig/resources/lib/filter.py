from resources.lib.xbianconfig import xbianConfig

# define filter here
# TO DO if necessary, make a plung'n play Filter directory like category


def BTRFS():
    return xbianConfig(cmd=["df -T | grep '/$' | awk '{print $2}'"])[0] == 'btrfs'


def RPI():
    return xbianConfig(cmd=["xbian-arch"])[0] == 'RPI'


def IMX6():
    return xbianConfig(cmd=["xbian-arch"])[0] == 'IMX6'


class filters:
    # all filter is "AND" relation. it's enough for now
    # so all condition must be met for settings be activate
    # if a filter is not know at evaluate time, it will return false for setting

    def __init__(self):
        # create/read default filters here
        self.filters = {}
        self.filters['ALL'] = True
        self.filters['BTRFS'] = BTRFS()
        self.filters['RPI'] = RPI()
        self.filters['IMX6'] = IMX6()

    def is_active(self, filtres):
        active = True
        for filtre in filtres:
            if filtre[0] == '!':
                filtre = filtre[1:]
                opposite = True
            else:
                opposite = False

            if filtre in self.filters:
                if opposite:
                    active = active and not self.filters[filtre]
                else:
                    active = active and self.filters[filtre]
            else:
                active = False

            if not active:
                break
        return active

setting_filter = filters()
