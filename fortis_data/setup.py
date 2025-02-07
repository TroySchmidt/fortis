from setuptools import setup, find_packages

setup(
    name='fortis_data',
    version='0.1.0',
    packages=find_packages(), # Automatically find packages
    package_data={'': ['data/*.csv']},  # Include CSV files
    include_package_data=True, # Important!
    # ... other metadata ...
)