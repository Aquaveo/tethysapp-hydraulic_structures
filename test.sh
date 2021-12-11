#!/usr/bin/env bash
mkdir -p coverage
rm -f .coverage
echo "Running Tests..."
coverage run -a --rcfile=coverage.ini $1 test -v 2 tethysapp.hydraulic_structures.tests.integrated_tests
echo "Combined Coverage Report..."
coverage report --rcfile=coverage.ini
echo "Linting..."
flake8
echo "Testing Complete"