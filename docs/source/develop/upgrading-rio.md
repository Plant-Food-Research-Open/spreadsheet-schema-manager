# Upgrade Rio

Rio is pinned to an exact version in `requirements.txt`, since minor releases can change
behaviour the app or the end-to-end tests rely on.

1. Read what changed. If there are no release notes, diff the two published wheels.
2. Check the app for any removed or renamed API.
3. Check the end-to-end tests for Rio internals they depend on, such as the
   `<rio-pressable-element>` used in `tests/pages/base_page.py`.
4. Bump the pin, install, and run the unit tests.
5. Start the app and check it serves pages without errors.
6. Deploy to a test environment and run the end-to-end tests.
