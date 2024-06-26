# -*- coding: utf-8 -*-
#
# WDmodel documentation build configuration file, created by
# sphinx-quickstart on Sun May 28 12:08:59 2017.
#
# This file is execfile()d with the current directory set to its
# containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
import re

# We need the modules to be discoverable, regardless of which environment they
# are being built on, so we make sure the module directory is in sys.path
sys.path.insert(0, os.path.abspath('..'))

# Get mock if we are running python 2 or 3
try:
    from unittest.mock import MagicMock
except ImportError as e:
    from mock import Mock as MagicMock

class Mock(MagicMock):
    @classmethod
    def __getattr__(cls, name):
            return MagicMock()

# exclude modules that need C in some form or other from building using mock for ReadTheDocs compatability
MOCK_MODULES = ['numpy','numpy.polynomial','numpy.polynomial.polynomial',
                'scipy','scipy.stats','scipy.signal','scipy.interpolate','scipy.ndimage','scipy.ndimage.filters',
                'astropy','astropy.constants','astropy.visualization',
                'emcee','emcee.utils','emcee.ptsampler','emcee.autocorr',
                'celerite','celerite.modeling','astropy.table',
                'corner','extinction','h5py','iminuit','mpi4py','pysynphot','uncertainties',
                'matplotlib', 'matplotlib.mlab', 'matplotlib.pyplot','matplotlib.gridspec',
                'matplotlib.backends', 'matplotlib.backends.backend_pdf', 'matplotlib.font_manager']

sys.modules.update((mod_name, Mock()) for mod_name in MOCK_MODULES)


# -- General configuration ------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ['sphinx.ext.autodoc',
            'sphinx.ext.mathjax',
            'sphinx.ext.viewcode',
            'sphinx.ext.intersphinx',
            'sphinx.ext.napoleon']

autoclass_content = "class"
autdoc_member_order = "bysource"
autodoc_default_flags = ["members", "undoc-members"]
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = True

# allows us to link to other packages that we use
intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'numpy': ('https://docs.scipy.org/doc/numpy/', None),
    'scipy': ('https://docs.scipy.org/doc/scipy/reference/', None),
    'astropy': ('http://docs.astropy.org/en/stable/', None),
    'pysynphot': ('http://pysynphot.readthedocs.io/en/latest/', None),
    'iminuit': ('https://iminuit.readthedocs.io/en/stable/', None),
    'emcee': ('https://emcee.readthedocs.io/en/stable/', None),
    'mpi4py': ('https://mpi4py.readthedocs.io/en/stable/', None),
    'celerite': ('http://celerite.readthedocs.io/en/stable/', None),
    'matplotlib': ('https://matplotlib.org/', None),
    'corner': ('http://corner.readthedocs.io/en/stable/', None)
}


# skip documenting special methods except for init and call methods
def skip(app, what, name, obj, skip, options):
    if name.startswith("_"):
        if name.startswith("__init") or name == "__call__":
            return False
        if name.startswith("__"):
            pass
        else:
            return False
    return skip

def setup(app):
    app.connect("autodoc-skip-member", skip)


# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = u'WDmodel'
copyright = u'2019, Gautham Narayan'
author = u'Gautham Narayan'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.

dir_path = os.path.dirname(os.path.realpath(__file__))
init_string = open(os.path.join(dir_path, '..', 'WDmodel','__init__.py')).read()
VERS = r"^__version__\s+=\s+[\'\"]([0-9\.]*)[\'\"]$"
mo = re.search(VERS, init_string, re.M)
__version__ = mo.group(1)


# The short X.Y version.
version = __version__
# The full version, including alpha/beta/rc tags.
release = __version__

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = False


# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
html_theme_options = {
    'collapse_navigation': False,
    'navigation_depth': 4,
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
#html_static_path = ['_static']


# -- Options for HTMLHelp output ------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = 'WDmodeldoc'


# -- Options for LaTeX output ---------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #
    # 'papersize': 'letterpaper',

    # The font size ('10pt', '11pt' or '12pt').
    #
    # 'pointsize': '10pt',

    # Additional stuff for the LaTeX preamble.
    #
    # 'preamble': '',

    # Latex figure (float) alignment
    #
    # 'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, 'WDmodel.tex', u'WDmodel Documentation',
     u'Gautham Narayan', 'manual'),
]


# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, 'wdmodel', u'WDmodel Documentation',
     [author], 1)
]


# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (master_doc, 'WDmodel', u'WDmodel Documentation',
     author, 'WDmodel', 'One line description of project.',
     'Miscellaneous'),
]

html_context = {
    "display_github": True,  # Integrate GitHub
    "github_user": "gnarayan",  # Username
    "github_repo": "WDmodel",   # Repo name
    "github_version": "master",  # Version
    "conf_py_path": "/docs/",  # Path in the checkout to the docs root
}
