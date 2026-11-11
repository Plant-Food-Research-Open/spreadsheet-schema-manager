# Write these docs

The docs are written in Markdown (MyST) in `docs/source/` and built with Sphinx. Read the Docs
builds them from `.readthedocs.yaml` on every push to `main`.

Build and preview locally:

```bash
pip install -r docs/requirements.txt
sphinx-build -W -b html docs/source docs/_build/html
```

`-W` turns warnings into errors, as on Read the Docs. Open `docs/_build/html/index.html` to
preview.

- **Release notes** are generated from `spreadsheet_schema_manager_rio/release_notes.py`, the
  same source as the in-app release notes. Edit that file, not the generated page.
- **Tutorial data** lives in `docs/source/_static/tutorial-data/`.
