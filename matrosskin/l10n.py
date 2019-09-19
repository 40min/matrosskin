import os
import sys
import locale
import gettext


def lang_init():
    """
    Initialize a translation framework (gettext).
    Typical use::
        _ = lang_init()

    :return: A string translation function.
    :rtype: (str) -> str
    """
    _locale, _encoding = locale.getdefaultlocale()  # Default system values

    path = sys.argv[0]
    path = os.path.join(os.path.dirname(path), 'locale')

    lang = gettext.translation('matrosskin', path, [_locale])
    return lang.gettext


_ = lang_init()
