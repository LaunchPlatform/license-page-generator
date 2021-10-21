import collections
import csv
import datetime
import logging
import time
import typing

import click

from .github_repo import extract_license
from .github_repo import extract_repo_from_url
from .github_repo import License
from .github_repo import RateLimitError
from .npm import BlockedError
from .npm import extract_repo as extract_npm_repo


@click.command()
@click.argument("INPUT_FILE", type=click.Path(exists=True))
@click.option(
    "--input-encoding", default="utf16", type=str, help="Input file encoding."
)
@click.option(
    "-d",
    "--disable-cache",
    is_flag=True,
    help="Disable HTTP request cache.",
)
@click.option(
    "-s",
    "--suppress-retry-failure",
    is_flag=False,
    help="Suppress retry failures.",
)
def main(
    input_file: str,
    input_encoding: str,
    disable_cache: bool,
    suppress_retry_failure: bool,
):
    logger = logging.getLogger(__name__)
    packages = collections.defaultdict(dict)
    with open(input_file, "rt", encoding=input_encoding) as fo:
        reader = csv.reader(fo)
        # Skip the header line
        next(reader)
        for row in reader:
            (
                name,
                version,
                directory,
                repo,
                summary,
                from_pkg,
                from_license,
                from_readme,
            ) = row[:8]
            packages[name]["repo"] = repo
            licenses = filter(lambda l: len(l), [from_pkg, from_license, from_readme])
            logger.debug("Get package %s licenses %s", name, licenses)
            packages[name]["licenses"] = (
                packages[name].get("licenses", set()).union(set(licenses))
            )
    sorted_names = sorted(list(packages.keys()))
    use_cache = not disable_cache
    for name in sorted_names:
        pkg: typing.Dict = packages[name]
        repo: typing.Optional[str] = extract_repo_from_url(pkg["repo"])
        if repo is None:
            logger.info(
                "No repo name for %s pkg, extracting from npm, use_cache=%s",
                name,
                use_cache,
            )

            for retry_count in range(3):
                try:
                    repo = extract_npm_repo(name, use_cache=use_cache)
                    break
                except BlockedError:
                    logger.warning(
                        "Blocked by cloudflare, sleep for a while and try again later"
                    )
                    time.sleep(60)
                    continue
            if repo is None:
                if retry_count == 3 and not suppress_retry_failure:
                    raise RuntimeError("Failed to get npm repo")
                logger.info("Cannot extract repo name from npm for %s", name)
                print(name, "=>", pkg)
                continue
            else:
                logger.info("Extracted repo name %s from npm for %s", repo, name)
                repo = extract_repo_from_url(repo)
        logger.info(
            "Extracting license from GitHub for %s, use_cache=%s", name, use_cache
        )
        license: typing.Optional[License] = None
        for retry_count in range(3):
            try:
                license = extract_license(repo, use_cache=use_cache)
                logger.info("Extracted license %s from GitHub for %s", license, name)
                break
            except RateLimitError as error:
                now = datetime.datetime.now()
                delta = error.reset_timestamp - now
                logger.warning(
                    "Rate limited, sleep for %s seconds and try again",
                    delta.total_seconds(),
                )
                time.sleep(delta.total_seconds())
                continue

        if retry_count == 3 and not suppress_retry_failure:
            raise RuntimeError("Failed to get github repo")
        print(name, "=>", license)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
