import dataclasses
import datetime
import os
import typing
import urllib.parse

import requests
from requests.auth import HTTPBasicAuth

from .http_cache import get_cache_session


GITHUB_SSH_REPO_PREFIX = "git@github.com:"


class RateLimitError(Exception):
    def __init__(self, reset_timestamp: datetime.datetime, msg: str):
        super().__init__(msg)
        self.reset_timestamp = reset_timestamp


@dataclasses.dataclass
class License:
    key: typing.Optional[str]
    name: typing.Optional[str]
    url_to_license: typing.Optional[str]


def extract_repo_from_url(repo_or_url: str) -> typing.Optional[str]:
    """Extract repo "{owner}/{name}" from a given GitHub repo or url

    :param repo_or_url: repo or url to prase, or "(none)" means None
    :return: extracted repo "{owner}/{name}" or None value if cannot be found
    """
    if repo_or_url == "(none)":
        return None
    if repo_or_url.startswith(GITHUB_SSH_REPO_PREFIX):
        return repo_or_url.removeprefix(GITHUB_SSH_REPO_PREFIX)
    parsed = urllib.parse.urlparse(repo_or_url)
    if parsed.scheme is None:
        return repo_or_url
    if parsed.hostname is not None and parsed.hostname.lower() != "github.com":
        return None
    path = parsed.path.lstrip("/")
    return "/".join(path.split("/")[:2])


# Use GitHub license API
# ref: https://docs.github.com/en/rest/reference/licenses
def extract_license(repo: str, use_cache: bool = False) -> License:
    """Extract license information for a given repo

    :param repo: name of repo, in "{owner}/{name}" format
    :param use_cache: use http cache or not
    :return: the extracted License object
    """
    url = urllib.parse.urljoin("https://api.github.com/repos/", f"{repo}/license")
    auth: typing.Optional[HTTPBasicAuth] = None
    github_user = os.environ.get("GITHUB_USER")
    github_token = os.environ.get("GITHUB_TOKEN")
    if github_user is not None and github_token is not None:
        auth = HTTPBasicAuth(username=github_user, password=github_token)

    session: requests.Session = requests.Session()
    if use_cache:
        session = get_cache_session()

    resp: requests.Response = session.get(
        url, headers={"Accept": "application/vnd.github.v3+json"}, auth=auth
    )
    if resp.status_code == 404:
        return License(key=None, name=None, url_to_license=None)
    if resp.status_code == 403 and resp.json().get("message", "").startswith(
        "API rate limit exceeded"
    ):
        reset_timestamp = int(resp.headers["X-RateLimit-Reset"])
        raise RateLimitError(
            msg="Rate limit exceeded",
            reset_timestamp=datetime.datetime.fromtimestamp(reset_timestamp),
        )
    body: typing.Dict = resp.json()
    url_to_license: typing.Optional[str] = body.get("html_url")
    key: typing.Optional[str] = None
    name: typing.Optional[str] = None
    if "license" in body:
        key = body["license"].get("key")
        name = body["license"].get("name")
    return License(
        key=key,
        name=name,
        url_to_license=url_to_license,
    )
