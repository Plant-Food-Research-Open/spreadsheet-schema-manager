# Testing

## Unit tests

Unit tests live in `tests/` and use Python's `unittest`:

```bash
python -m unittest discover -s tests
```

## End-to-end tests

Browser-level tests are in the companion repository
[spreadsheet-schema-manager-tests](https://github.com/Plant-Food-Research-Open/spreadsheet-schema-manager-tests),
written with Playwright and pytest. They run against a
deployed instance running with `AUTH_DISABLED=true`; set its URL in `BASE_URL`.
