# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'ga4_data_import'
copyright = '2023, Max Ostapenko'
author = 'Max Ostapenko'
release = '0.1.56'

import os
import sys

sys.path.insert(0, os.path.abspath('../..'))

# Path to the source files
source_dir = os.path.abspath('.')

# Path to the build directory
build_dir = os.path.abspath('../../docs/build')


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.coverage', 'sphinx.ext.napoleon',]
napoleon_google_docstring = True

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']
html_relative_path = '../..'
html_theme_options = {
    'github_user': 'max_ostapenko',
    'github_repo': 'ga4_data_import',
    'github_banner': True,
    'show_related': True,
}
