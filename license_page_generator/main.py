import collections
import csv
import datetime
import logging
import time
import typing

import click

from .github_repo import extract_license
from .github_repo import extract_repo as extract_github_repo
from .github_repo import RateLimitError
from .npm import extract_repo as extract_npm_repo


@click.command()
@click.argument("INPUT_FILE", type=click.Path(exists=True))
@click.option(
    "--input-encoding", default="utf16", type=str, help="Input file encoding."
)
def main(input_file: str, input_encoding: str):
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
    for name in sorted_names:
        pkg: typing.Dict = packages[name]
        repo: typing.Optional[str] = extract_github_repo(pkg["repo"])
        if repo is None:
            logger.info("No repo name for %s pkg, extracting from npm ...", name)
            repo = extract_npm_repo(name)
            if repo is None:
                logger.info("Cannot extract repo name from npm for %s", name)
                print(name, "=>", pkg)
                continue
            else:
                logger.info("Extracted repo name %s from npm for %s", repo, name)
                repo = extract_github_repo(repo)
        for _ in range(3):
            try:
                license = extract_license(repo)
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

        print(name, "=>", license)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
