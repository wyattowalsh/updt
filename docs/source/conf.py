"""Sphinx configuration for updt documentation."""

import sys
from pathlib import Path

# Add src to path for autodoc
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

# -- Project information -----------------------------------------------------
project = "updt"
copyright = "2024, updt contributors"
author = "updt contributors"
release = "0.1.0"
version = "0.1.0"

# -- General configuration ---------------------------------------------------
extensions = [
    # Core / structure
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    "sphinx.ext.coverage",
    "sphinx.ext.extlinks",
    # Markdown
    "myst_parser",
    # Authoring UX / components
    "sphinx_copybutton",
    "sphinx_design",
    "sphinx_tabs.tabs",
    "sphinx_togglebutton",
    "sphinxemoji.sphinxemoji",
    # Diagrams
    "sphinxcontrib.mermaid",
    # API & typing quality
    "autodoc2",
    "sphinx_autodoc_typehints",
    "autoclasstoc",
    # CLIs
    "sphinx_click",
    # Data/standards
    "sphinx-jsonschema",
    "sphinxcontrib.httpdomain",
    # Repo-aware / meta
    "sphinx_git",
    # Hover references
    "hoverxref.extension",
    # SEO
    "sphinx_sitemap",
    "notfound.extension",
]

source_suffix = {".rst": "restructuredtext", ".md": "markdown", ".txt": "markdown"}
templates_path = ["_templates"]
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    "**/.ipynb_checkpoints",
    "**/__pycache__/**",
]

# -- MyST configuration ------------------------------------------------------
myst_enable_extensions = [
    "attrs_block",
    "attrs_inline",
    "colon_fence",
    "deflist",
    "fieldlist",
    "tasklist",
    "dollarmath",
    "amsmath",
    "linkify",
    "substitution",
    "html_image",
    "replacements",
    "smartquotes",
]
myst_heading_anchors = 3
myst_links_external_new_tab = True

# -- HTML output -------------------------------------------------------------
html_theme = "shibuya"
html_title = f"{project} {release}"
html_short_title = "updt"
html_static_path = ["_static"]
html_css_files = [
    "css/design-tokens.css",
    "css/custom.css",
    "css/components.css",
]
html_js_files = ["js/custom.js"]
html_favicon = "_static/img/favicon/favicon.ico"

html_theme_options = {
    "nav_title": "updt",
    "github_url": "https://github.com/wyattowalsh/updt",
    "accent_color": "teal",
    "dark_code": False,
    "color_mode": "auto",
    "globaltoc_collapse": True,
    "toctree_collapse": True,
    "toctree_maxdepth": 4,
    "toctree_titles_only": False,
    "toctree_includehidden": True,
    "nav_links": [
        {"title": "📖 Guides", "url": "guides/index"},
        {"title": "🧰 CLI", "url": "cli"},
        {"title": "📚 API", "url": "api/index"},
        {"title": "📝 Changelog", "url": "changelog"},
    ],
}

# -- API documentation (autodoc2) --------------------------------------------
autodoc2_output_dir = "reference"
autodoc2_render_plugin = "myst"
autodoc2_module_all_regexes = [r".*"]
autodoc2_docstring_parser_regexes = [(r".*", "myst")]
autodoc2_hidden_objects = ["dunder", "private"]
autodoc2_skip_module_regexes = [
    r".*\.tests?\..*",
    r".*\.test_.*",
    r".*__pycache__.*",
]
autodoc2_hidden_regexes = [r".*\._.*"]
autodoc2_class_docstring = "merge"
autodoc2_docstrings = "all"
autodoc2_packages = [
    {
        "path": "../../src/updt",
        "exclude": [r".*tests?.*", r".*build.*", r".*dist.*"],
        "auto_mode": True,
    },
]

# -- Autodoc & autosummary ---------------------------------------------------
autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "special-members": "__init__",
    "undoc-members": True,
    "exclude-members": "__weakref__",
}
autosummary_generate = True
autosummary_generate_overwrite = False
autosummary_imported_members = True

# -- Napoleon (docstring styles) --------------------------------------------
napoleon_numpy_docstring = True
napoleon_google_docstring = True
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_type_aliases = None

# -- Type hints --------------------------------------------------------------
autodoc_typehints = "description"
autodoc_typehints_description_target = "documented"
typehints_use_signature = True
typehints_use_signature_return = True
always_document_param_types = True

# -- Class sections ----------------------------------------------------------
autoclasstoc_sections = [
    "public-attrs",
    "public-methods",
    "private-attrs",
    "private-methods",
]

# -- Copy button -------------------------------------------------------------
copybutton_prompt_text = r">>> |\.\.\. |\$ "
copybutton_prompt_is_regexp = True
copybutton_remove_prompts = True
copybutton_only_copy_prompt_lines = False
copybutton_line_continuation_character = "\\"
copybutton_selector = "div.highlight pre"
copybutton_copy_empty_lines = True
copybutton_here_doc_delimiter = "EOF"

# -- Mermaid diagrams --------------------------------------------------------
mermaid_version = "11.12.1"
mermaid_output_format = "svg"
mermaid_d3_zoom = True

# -- Intersphinx -------------------------------------------------------------
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master", None),
    "typer": ("https://typer.tiangolo.com", None),
    "pydantic": ("https://docs.pydantic.dev/latest", None),
    "rich": ("https://rich.readthedocs.io/en/stable", None),
    "loguru": ("https://loguru.readthedocs.io/en/stable", None),
}
intersphinx_timeout = 30

# -- Hoverxref ---------------------------------------------------------------
hoverxref_auto_ref = True
hoverxref_domains = ["py"]
hoverxref_roles = ["option", "doc"]
hoverxref_role_types = {
    "mod": "modal",
    "class": "tooltip",
    "func": "tooltip",
    "meth": "tooltip",
    "attr": "tooltip",
    "exc": "tooltip",
    "obj": "tooltip",
}

# -- Sitemap & SEO -----------------------------------------------------------
html_baseurl = "https://wyattowalsh.github.io/updt/"
sitemap_url_scheme = "{link}"

# -- 404 page ----------------------------------------------------------------
notfound_context = {
    "title": "Page Not Found",
    "body": "<h1>404 - Page Not Found</h1><p>Use search or the left ToC.</p>",
}
notfound_template = "page.html"
notfound_pagename = "404"
notfound_urls_prefix = "/"

# -- External links ----------------------------------------------------------
extlinks = {
    "issue": ("https://github.com/wyattowalsh/updt/issues/%s", "issue %s"),
    "pr": ("https://github.com/wyattowalsh/updt/pull/%s", "PR %s"),
}

# -- Quality & link checking -------------------------------------------------
nitpicky = False
suppress_warnings = ["autodoc2.*", "myst.header"]
linkcheck_ignore = [r"^http://localhost", r"^https://localhost"]

# -- Todo extension ----------------------------------------------------------
todo_include_todos = True
