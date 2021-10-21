import pytest

from license_page_generator.npm import extract_repo


@pytest.mark.parametrize(
    "pkg_name, repo_url",
    [
        ("avataaars", "https://github.com/fangpenlin/avataaars"),
    ],
)
def test_extract_repo(pkg_name: str, repo_url: str):
    assert extract_repo(pkg_name) == repo_url
