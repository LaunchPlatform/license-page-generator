import dataclasses
import typing
import urllib.parse

import requests


@dataclasses.dataclass
class License:
    key: typing.Optional[str]
    name: typing.Optional[str]
    url_to_license: typing.Optional[str]


# Use GitHub license API
# ref: https://docs.github.com/en/rest/reference/licenses
def extract_repo_license(repo: str) -> License:
    url = urllib.parse.urljoin("https://api.github.com/repos/", f"{repo}/license")
    resp: requests.Response = requests.get(
        url, headers={"Accept": "application/vnd.github.v3+json"}
    )
    resp.raise_for_status()
    body: typing.Dict = resp.json()
    key: typing.Optional[str] = None
    name: typing.Optional[str] = None
    url_to_license: typing.Optional[str] = None
    if "license" in body:
        key = body["license"].get("key")
        name = body["license"].get("name")
    url_to_license = body.get("html_url")
    return License(
        key=key,
        name=name,
        url_to_license=url_to_license,
    )
