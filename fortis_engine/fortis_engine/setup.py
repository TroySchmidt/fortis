from setuptools import setup, find_packages

setup(
    name='fortis_engine',
    version='0.1.0',
    description='Engine for risk assessment using Hazus methodology.',
    author='Troy Schmidt',
    author_email='tschmidt@niyamit.com',
    url='https://github.com/TroySchmidt/fortis_engine',  # Update with your repository URL
    packages=find_packages(),  # Automatically discovers all packages and subpackages
    install_requires=[
        'pandas>=1.0.0',
        'geopandas>=0.8.0',
        'fortis_data>=0.1.0',  # This ensures the official version of fortis_data is installed as a dependency.
    ],
    include_package_data=True,  # Include non-code files (if specified in MANIFEST.in)
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',  # or any version you support
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',  # Adjust based on your minimum Python version requirement.
)
