import io
import typing
import urllib.parse

import requests
from lxml import etree

from .http_cache import get_cache_session


class BlockedError(Exception):
    pass


def extract_repo(pkg_name: str, use_cache: bool = False) -> typing.Optional[str]:
    """Extract repo URL from npm web page

    :param pkg_name: package name
    :param use_cache: use http cache or not
    :return:
    """
    url = urllib.parse.urljoin("https://www.npmjs.com/package/", pkg_name)

    session: requests.Session = requests.Session()
    if use_cache:
        session = get_cache_session()

    resp: requests.Response = session.get(url)
    if resp.status_code == 429:
        raise BlockedError("Blocked by cloudflare, try again later")
    resp.raise_for_status()

    parser = etree.HTMLParser()
    tree = etree.parse(io.StringIO(resp.text), parser)
    result = tree.xpath("string(//a[@aria-labelledby='repository']/@href)")
    if not result:
        return None
    return "".join(result).strip()
