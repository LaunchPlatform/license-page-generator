# license-page-generator
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

# Output CSV file format

There are a few columns in the CSV output file:

- `name`: name of the package
- `license`: License name of the package (if available)
- `license_url`: URL to the license file (if available)

Here's an example:

```csv
name,license,license_url
@babel/code-frame,MIT License,https://github.com/babel/babel/blob/main/LICENSE
@babel/compat-data,MIT License,https://github.com/babel/babel/blob/main/LICENSE
@babel/core,MIT License,https://github.com/babel/babel/blob/main/LICENSE
@babel/generator,MIT License,https://github.com/babel/babel/blob/main/LICENSE
@jest/console,MIT License,https://github.com/facebook/jest/blob/main/LICENSE
@jest/fake-timers,MIT License,https://github.com/facebook/jest/blob/main/LICENSE
@jest/source-map,MIT License,https://github.com/facebook/jest/blob/main/LICENSE
@jest/test-result,MIT License,https://github.com/facebook/jest/blob/main/LICENSE
@jest/types,MIT License,https://github.com/facebook/jest/blob/main/LICENSE
@nodelib/fs.scandir,MIT License,https://github.com/nodelib/nodelib/blob/master/LICENSE
@nodelib/fs.stat,MIT License,https://github.com/nodelib/nodelib/blob/master/LICENSE
@nodelib/fs.walk,MIT License,https://github.com/nodelib/nodelib/blob/master/LICENSE
@react-native-async-storage/async-storage,MIT License,https://github.com/react-native-async-storage/async-storage/blob/master/LICENSE
@react-native-community/cli,MIT License,https://github.com/react-native-community/cli/blob/master/LICENSE
@react-native-community/cli-debugger-ui,MIT License,https://github.com/react-native-community/cli/blob/master/LICENSE
@react-native-community/cli-hermes,MIT License,https://github.com/react-native-community/cli/blob/master/LICENSE
@react-native-community/cli-platform-android,MIT License,https://github.com/react-native-community/cli/blob/master/LICENSE
@react-native-community/cli-platform-ios,MIT License,https://github.com/react-native-community/cli/blob/master/LICENSE
@react-native-community/cli-server-api,MIT License,https://github.com/react-native-community/cli/blob/master/LICENSE
@react-native-community/cli-tools,MIT License,https://github.com/react-native-community/cli/blob/master/LICENSE
@react-native-community/cli-types,MIT License,https://github.com/react-native-community/cli/blob/master/LICENSE
abort-controller,MIT License,https://github.com/mysticatea/abort-controller/blob/master/LICENSE
absolute-path,MIT License,https://github.com/filearts/node-absolute-path/blob/master/LICENSE
accepts,MIT License,https://github.com/jshttp/accepts/blob/master/LICENSE
anser,MIT License,https://github.com/IonicaBizau/anser/blob/master/LICENSE
ansi-colors,MIT License,https://github.com/doowb/ansi-colors/blob/master/LICENSE
ansi-cyan,MIT License,https://github.com/jonschlinkert/ansi-cyan/blob/master/LICENSE
ansi-escapes,MIT License,https://github.com/sindresorhus/ansi-escapes/blob/main/license
```

# Generate Markdown page

To generate a markdown page, you can run command like this

```bash
poetry run python -m license_page_generator.gen_markdown output.csv
```
