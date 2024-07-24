# docs/conf.py
import os
import sys

# Add the path to the 'precalc' directory to sys.path
sys.path.insert(0, os.path.abspath('../'))
sys.path.insert(0, os.path.abspath('../../'))

# -- Project information -----------------------------------------------------

project = 'Poseidon-Viewer'
copyright = '2024, Poseidon Project Group'
author = 'Wenrui Jiang, Dmitry Medvedev, Thomas Haine'

# -- General configuration ---------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',  # If you use Google or NumPy style docstrings
]

templates_path = ['_templates']
exclude_patterns = []

# -- Options for autodoc ------------------------------------------------------

autodoc_member_order = 'groupwise'

# -- Options for HTML output -------------------------------------------------

html_theme = 'sphinx_book_theme'

html_theme_options = {
    'navigation_with_keys': False,
}

html_static_path = ['_static']

