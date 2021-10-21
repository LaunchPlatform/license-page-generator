import typing

import requests_cache

# Create session as a global variable brings in many side effects such as creating
# files when module imported, it seems like a bad idea so that we are using lazy
# creation here by get_cache_session instead
_session: typing.Optional[requests_cache.CachedSession] = None


def get_cache_session() -> requests_cache.CachedSession:
    global _session
    if _session is None:
        _session = requests_cache.CachedSession(__name__)
    return _session
