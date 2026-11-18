"""Sphinx configuration for the normative modelling toolkit docs."""
from __future__ import annotations

project = "Normative modelling toolkit"
copyright = "2026"
author = "Normative contributors"
release = "0.1.0"
version = "0.1"

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.mathjax",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "dollarmath",
    "fieldlist",
]

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

root_doc = "index"
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    "requirements.txt",
]

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_title = "Normative modelling toolkit"
html_short_title = "Normative"
html_show_sourcelink = True

html_theme_options = {
    "collapse_navigation": False,
    "navigation_depth": 3,
    "titles_only": False,
}

# Sidebar + page header: "Edit on GitHub" / source repo link (sphinx_rtd_theme)
html_context = {
    "display_github": True,
    "github_user": "phindagijimana",
    "github_repo": "normative",
    "github_version": "main",
    "conf_py_path": "/docs/",
}

myst_heading_anchors = 3
