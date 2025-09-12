"""
WSGI config for Yatra_darshan project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""
import hashlib
try:
    # test platform support for the 'usedforsecurity' kwarg
    hashlib.md5(b"test", usedforsecurity=False)
except TypeError:
    _orig_md5 = hashlib.md5
    def _md5_wrapper(data=b"", *args, **kwargs):
        # silently drop unsupported kwarg and call original
        kwargs.pop("usedforsecurity", None)
        return _orig_md5(data, *args, **kwargs)
    hashlib.md5 = _md5_wrapper
# ---- end: compatibility shim ----

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Yatra_darshan.settings')

application = get_wsgi_application()

