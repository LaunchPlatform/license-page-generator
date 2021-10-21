import io
import typing
import urllib.parse

import requests
from lxml import etree


def extract_repo(pkg_name: str) -> typing.Optional[str]:
    url = urllib.parse.urljoin("https://www.npmjs.com/package/", pkg_name)
    resp: requests.Response = requests.get(url)

    parser = etree.HTMLParser()
    tree = etree.parse(io.StringIO(resp.text), parser)
    result = tree.xpath("string(//a[@aria-labelledby='repository']/@href)")
    if not result:
        return None
    return "".join(result).strip()
