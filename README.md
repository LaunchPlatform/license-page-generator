# node-pkg-oss-license-page-generator
A simple Python command line tool for generating Open Source License page for node JS packages

| :warning: DISCLAIMER                                                   |
|:-----------------------------------------------------------------------|
| This is just a tool we build at Launch Platform for helping ourselves making used package Open Source license page easier. We thought it might be useful to others so that we opened source it here. This is not a legal advice. For how you should distribute your software with open source license, please consult a lawyer. Also there's no guarantee of accuracy of the result from this tool, please use it at your own risk. |

## Usage

You need to install [Node License Finder (nlf)](https://www.npmjs.com/package/nlf)
and use it to dump the licenses CSV file of used packages first in your
nodejs project folder. Like this

```bash
nlf -c --no-dev > licenses.csv
```

Then clone this repo and run

```bash
poetry install
```

then 

```bash
poetry run python -m license_page_generator.main licenses.csv output.csv
```

This tool reads GitHub API, and obviously GitHub API is rate limited, to
increase the rate limit, you can expose environment variables:

- `GITHUB_USER` - your GitHub username
- `GITHUB_TOKEN` - a valid token for accessing GitHub API

With that the command line tool will use it for accessing GitHub API on
behavior of your user account and thus the rate limit will be increased.

This tool also reads web page from NPM when the GitHub repo is unknown to nlf,
and if we are sending requests to frequent, we may get blocked by Cloudflare
for accessing npmjs.com. This tool is designed to be able to resume progress
by reading the same output CSV file. You can always stop the script
and run it again, or remove a row from the output csv file and run command again.

