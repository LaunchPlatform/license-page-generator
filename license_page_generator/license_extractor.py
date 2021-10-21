import dataclasses
import typing

import requests


@dataclasses.dataclass
class License:
    type: typing.Optional[str]
    url_to_license: typing.Optional[str]


def extract_repo_license(repo: str) -> License:
    pass
