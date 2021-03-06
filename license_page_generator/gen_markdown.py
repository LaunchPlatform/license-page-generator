import click

from .main import read_output_file


PROJECT_NAME = "license-page-generator"
PROJECT_URL = "https://github.com/LaunchPlatform/license-page-generator"


@click.command()
@click.argument("INPUT_FILE", type=click.Path(exists=True))
@click.option(
    "-a",
    "--no-attribution",
    is_flag=True,
    help="Do not generate attribution to this tool",
)
@click.option(
    "-u",
    "--default-license-url",
    default="https://www.npmjs.com/package/{pkg_name}",
    type=str,
    help="Default license URL, as python new string format with pkg_name to be formatted",
)
def main(input_file: str, default_license_url: str, no_attribution: bool):
    packages = read_output_file(input_file)
    package_names = sorted(list(packages.keys()))
    for name in package_names:
        row = packages[name]
        license = row["license"]
        license_url = row.get("license_url", None)
        if license_url is None or not license_url.strip():
            license_url = default_license_url.format(pkg_name=name)
        print(f"- {name}: [{license}]({license_url})")

    if not no_attribution:
        print()
        print(f"This page is generated by [{PROJECT_NAME}]({PROJECT_URL})")


if __name__ == "__main__":
    main()
