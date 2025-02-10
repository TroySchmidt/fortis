ENVIRONMENT SETUP (for development, testing) IN VS CODE:

Clone repo from bash prompt
`git clone https://github.com/TroySchmidt/fortis.git`
`git config user.name "Your Name"`
`git config user.email "[email protected]"`

Test Explorer UI `uv venv` to create the virtual environment for the monorepo

Navigate to fortis_engine subfolder.  Run `uv pip install -e .[dev]` to install the required and development dependencies.

`uv run pytest .` to make sure the tests can run.

Example of building the package

`uvx --from build pyproject-build --installer=uv --outdir=dist --wheel libs/fortis-data`

Install the built packages

`uv pip install .\dist\*.whl`

Uninstall packages

`uv pip uninstall fortis.data`
