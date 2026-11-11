"""Sphinx configuration for the Spreadsheet Schema Manager docs."""

import importlib.util
from pathlib import Path

DOCS_SOURCE = Path(__file__).parent
REPO_ROOT = DOCS_SOURCE.parents[1]

project = "Spreadsheet Schema Manager"
copyright = (
    "2026, The New Zealand Institute for Bioeconomy Science Limited (Bioeconomy Science Institute)"
)
author = "Bioeconomy Science Institute"

extensions = [
    "myst_parser",
    "sphinx_copybutton",
    "sphinx.ext.githubpages",
]

myst_enable_extensions = ["colon_fence", "deflist"]
myst_heading_anchors = 3

source_suffix = {".md": "markdown"}
master_doc = "index"
exclude_patterns = ["_build"]

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_title = project
html_context = {
    "display_github": True,
    "github_user": "Plant-Food-Research-Open",
    "github_repo": "spreadsheet-schema-manager",
    "github_version": "main",
    "conf_py_path": "/docs/source/",
}


def _load_release_notes():
    """Import release_notes.py by path, so the docs build doesn't need the app's
    dependencies (importing the package itself would pull in Rio)."""
    path = REPO_ROOT / "spreadsheet_schema_manager_rio" / "release_notes.py"
    spec = importlib.util.spec_from_file_location("release_notes", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.RELEASE_NOTES


def _write_release_notes(app):
    lines = [
        "# Release notes",
        "",
        "Generated from `spreadsheet_schema_manager_rio/release_notes.py`, the same",
        "source as the in-app release notes.",
        "",
    ]
    for note in _load_release_notes():
        lines += [f"## {note.version} ({note.date})", ""]
        lines += [f"- {change}" for change in note.changes]
        lines.append("")
    out = DOCS_SOURCE / "about" / "release-notes.md"
    text = "\n".join(lines)
    # Only rewrite on change, so Sphinx doesn't rebuild the page every time.
    if not out.exists() or out.read_text() != text:
        out.write_text(text)


def setup(app):
    app.connect("builder-inited", _write_release_notes)
