import collections
import csv
import datetime
import logging
import os
import sys
import time
import typing

import click

from .github_repo import extract_license
from .github_repo import extract_repo_from_url
from .github_repo import License
from .github_repo import RateLimitError
from .npm import BlockedError
from .npm import extract_repo as extract_npm_repo

OUTPUT_FIELDS = ["name", "license", "license_url"]


def read_input_packages(
    input_file: str,
    input_encoding: str,
):
    logger = logging.getLogger(__name__)
    packages = collections.defaultdict(dict)
    with open(input_file, "rt", encoding=input_encoding) as in_fo:
        reader = csv.reader(in_fo)
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
            licenses = list(
                filter(lambda l: len(l.strip()), [from_pkg, from_license, from_readme])
            )
            logger.debug("Get package %s licenses %s", name, licenses)
            if licenses:
                packages[name].setdefault("licenses", licenses)
    return packages


def read_output_file(output_file: str) -> typing.Dict:
    with open(output_file, "rt", encoding="utf8") as fo:
        reader = csv.DictReader(fo, fieldnames=OUTPUT_FIELDS)
        next(reader)
        return {row["name"]: row for row in reader}


@click.command()
@click.argument("INPUT_FILE", type=click.Path(exists=True))
@click.argument("OUTPUT_FILE", type=click.Path())
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
    "--npm-sleep-time", default=10, type=int, help="Sleep time between npm fetch req."
)
def main(
    input_file: str,
    output_file: str,
    input_encoding: str,
    disable_cache: bool,
    npm_sleep_time: int,
):
    logger = logging.getLogger(__name__)

    finished_pkgs: typing.Dict = {}
    if os.path.exists(output_file):
        finished_pkgs = read_output_file(output_file)

    packages = read_input_packages(input_file, input_encoding)
    sorted_names = sorted(list(packages.keys()))
    use_cache = not disable_cache

    with open(output_file, "w") as out_fo:
        # Write finished pkgs to output file
        writer = csv.DictWriter(out_fo, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        finished_pkgs_names = sorted(list(finished_pkgs.keys()))
        for name in finished_pkgs_names:
            writer.writerow(finished_pkgs[name])
        out_fo.flush()
        for name in sorted_names:
            if name in finished_pkgs:
                logger.info("Skip finished pkg %s", name)
                continue
            pkg: typing.Dict = packages[name]
            first_input_license = pkg.get("licenses", [""])[0]
            repo: typing.Optional[str] = extract_repo_from_url(pkg["repo"])
            if repo is None:
                logger.info(
                    "No repo name for %s pkg, extracting from npm, use_cache=%s",
                    name,
                    use_cache,
                )

                try:
                    repo = extract_npm_repo(name, use_cache=use_cache)
                except BlockedError:
                    logger.warning(
                        "Blocked by cloudflare for fetching NPM page, please increase npm "
                        "sleep time or try again later"
                    )
                    sys.exit(1)
                if repo is None:
                    logger.info("Cannot extract repo name from npm for %s", name)
                    writer.writerow(
                        dict(name=name, license=first_input_license, license_url="")
                    )
                    out_fo.flush()
                    continue
                else:
                    logger.info("Extracted repo name %s from npm for %s", repo, name)
                    repo = extract_repo_from_url(repo)
                # Sleep a while for npm to avoid blocking
                time.sleep(npm_sleep_time)
            logger.info(
                "Extracting license from GitHub for %s, use_cache=%s", name, use_cache
            )
            license: typing.Optional[License] = None
            for retry_count in range(3):
                try:
                    license = extract_license(repo, use_cache=use_cache)
                    logger.info(
                        "Extracted license %s from GitHub repo %s for %s",
                        license,
                        repo,
                        name,
                    )
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

            if retry_count == 3:
                raise RuntimeError("Failed to get github repo, please try again later")
            writer.writerow(
                dict(
                    name=name,
                    license=license.name or first_input_license,
                    license_url=license.url_to_license,
                )
            )
            out_fo.flush()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
