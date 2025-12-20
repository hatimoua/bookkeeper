# Package Management

`requirements.txt` is a some what legacy way to retain packages. Poetry solved a lot of problems with it, then "uv" has become more popular in recent times -- they do a better job resolving packages and storing/sharing the dependencies (via the lock file).

The `pyproject.toml` file is also a more modern construct, historically each tool (formatter, linter, etc.) would have its own config file, but most tools now support the unified toml format so all configs can be collected in one place.

## Usage

1. `pip install uv`
2. `uv init`
3. `uv add <package>`
4. `uv add <package> --group=dev`
5. `uv sync`

#4 is great, you can install requirements you use locally (linters, formatters, stubs, etc.) that aren't needed in a deployed version - or install some just in a prototyping frame / etc.