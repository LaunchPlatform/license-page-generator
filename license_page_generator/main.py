import collections
import csv
import datetime
import logging
import time
import typing

import click

from .github_repo import extract_license
from .github_repo import extract_repo
from .github_repo import RateLimitError


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
        repo: typing.Optional[str] = extract_repo(pkg["repo"])
        if repo is None:
            print(name, "=>", pkg)
        else:
            for _ in range(3):
                try:
                    license = extract_license(repo)
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
