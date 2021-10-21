import collections
import csv

import click


@click.command()
@click.argument("INPUT_FILE", type=click.Path(exists=True))
@click.option(
    "--input-encoding", default="utf16", type=str, help="Input file encoding."
)
def main(input_file: str, input_encoding: str):
    packages = collections.defaultdict(dict)
    with open(input(), "rt", encoding=input_encoding) as fo:
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
            print(name, version, repo, summary, from_pkg, from_license, from_readme)
            packages[name]["repo"] = repo
            licenses = filter(lambda l: len(l), [from_pkg, from_license, from_readme])
            packages[name]["licenses"] = (
                packages[name].get("licenses", set()).union(set(licenses))
            )
    for name, pkg in packages.items():
        print(name, "=>", pkg)


if __name__ == "__main__":
    main()
