# Risk Assessment Engine

## ⚙️ Getting Started

### Jupyter Notebook
Sample notebook running Hawaii data with the FAST depth grid.

<a target="_blank" href="https://colab.research.google.com/github/TroySchmidt/fortis/blob/feat/college-demo/FAST_NSI_Example.ipynb">
  <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/>
</a>

### Installation

1. Install Python 3.10 or later. [Guide](https://www.tutorialsteacher.com/python/install-python).

2. Install uv. [Install Instructions](https://docs.astral.sh/uv/getting-started/installation/).

3. Clone the project and navigate to the directory:

    ```bash
    git clone https://github.com/TroySchmidt/fortis.git
    cd fortis
    ```

4. Install dependencies required and for development.

    ```bash
    uv sync --all-packages
    ```

5. Run a sample:

    ```bash
    uv run .\examples\fast.py
    ```

## Developer notes

ENVIRONMENT SETUP (for development, testing) IN VS CODE:

Clone repo from bash prompt
`git clone https://github.com/TroySchmidt/fortis.git`
`git config user.name "Your Name"`
`git config user.email "[email protected]"`

Test Explorer UI `uv venv` to create the virtual environment for the monorepo

Navigate to fortis_engine subfolder.  Run `uv pip install -e .[dev]` to install the required and development dependencies.

`uv run pytest .` to make sure the tests can run.

`uv sync --all-packages`

Example of building the package

`uvx --from build pyproject-build --installer=uv --outdir=dist --wheel libs/fortis-data`

Install the built packages

`uv pip install .\dist\*.whl`

Uninstall packages

`uv pip uninstall fortis.data`
