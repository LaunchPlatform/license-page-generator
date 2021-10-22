import pytest

from license_page_generator.github_repo import extract_license
from license_page_generator.github_repo import extract_repo_from_url
from license_page_generator.github_repo import License


@pytest.mark.parametrize(
    "repo_or_url, result",
    [
        ("(none)", None),
        ("launchplatform/monoline", "launchplatform/monoline"),
        ("https://github.com/launchplatform/monoline", "launchplatform/monoline"),
        ("https://github.com/launchplatform/monoline/", "launchplatform/monoline"),
        (
            "https://github.com/launchplatform/monoline/foo/bar",
            "launchplatform/monoline",
        ),
        ("https://gitlab.com/launchplatform/monoline", None),
    ],
)
def test_extract_repo(repo_or_url: str, result: str):
    assert extract_repo_from_url(repo_or_url) == result


@pytest.mark.parametrize(
    "repo, expected_license",
    [
        (
            "launchplatform/node-pkg-oss-license-page-generator",
            License(
                key="mit",
                name="MIT License",
                url_to_license="https://github.com/LaunchPlatform/node-pkg-oss-license-page-generator/blob/master/LICENSE",
            ),
        )
    ],
)
def test_extract_license(repo: str, expected_license: License):
    assert extract_license(repo) == expected_license