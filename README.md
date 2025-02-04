ENVIRONMENT SETUP (for development, testing) IN VS CODE:

Clone repo from bash prompt
`git clone https://github.com/TroySchmidt/fortis.git`
`git config user.name "Your Name"`
`git config user.email "[email protected]"`

Test Explorer UI `uv venv` to create the virtual environment for the monorepo
Navigate to fortis_engine subfolder.  Run `uv pip install -e .[dev]` to install the required and development dependencies.
`uv build` to test that the fortis_engine folder can be built.
`uv run pytest tests/` to make sure the tests can run.

Activate environment
`Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`
`.\.venv\Scripts\activate`
