import os

EXTRA_PATH = 'extra'
__all__ = []


def extra():
    for module in os.listdir(os.path.dirname(__file__)):
        if module == '__init__.py' or module[-3:] != '.py':
            continue
        __all__.append(module[:-3])
    __all__.sort()

    settings = []
    for module in __all__:
        module = 'categories.extra.' + module
        setarray = __import__(module, globals(), locals(), [module])
        setarray = __import__(module, globals(), locals(), [module])
        settings.extend(getattr(setarray, 'settings'))
    return settings
