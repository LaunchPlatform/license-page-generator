import pytest

from license_page_generator.license_extractor import extract_repo_license
from license_page_generator.license_extractor import License


@pytest.mark.parametrize(
    "repo, expected_license",
    [
        (
            "launchplatform/node-pkg-oss-license-page-generator",
            License(
                type="MIT",
                url_to_license="https://github.com/LaunchPlatform/node-pkg-oss-license-page-generator/blob/master/LICENSE",
            ),
        )
    ],
)
def test_extract_repo_license(repo: str, expected_license: License):
    assert extract_repo_license(repo) == expected_license
