# Venv setup

1. Initiate venv:

   ```
   python -m venv .
   source bin/activate
   ```

2. Install portage from distfiles (also requires `wheel`):
   ```console
   pip install wheel
   pip install /var/cache/distfiles/portage-3.0.14.tar.bz2
   ```

3. Install the rest of requirements:

   ```
   pip install -r requirements/dev.txt
   ```

# Code style

[Black](https://black.readthedocs.io/)

# Testing

Uses `pytest` with `pytest-cov`, run through `coverage.sh`