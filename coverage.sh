#!/bin/sh

python -m pytest -s --cov=overlay_maintain_tools/ --cov-report term-missing --cov-config=.coveragerc
