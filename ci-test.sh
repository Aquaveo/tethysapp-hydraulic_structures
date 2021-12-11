#!/usr/bin/env bash
if [ ! -f "$1" ]; then
    echo "Usage: . test.sh [/path/to/manage.py]";
    return 1;
fi

# Reinstall in development so coverage will work
python setup.py develop

# Cleanup Previous Runs
rm -f /var/www/tethys/apps/tethysapp-hydraulic_structures/.coverage

echo "Running Tests..."
coverage run -a --rcfile=ci-coverage.ini $1 test tethysapp.hydraulic_structures.tests.integrated_tests
intermediate_ret_val=$?

# Minimum Required Coverage
minimum_required_coverage=0
coverage report -m --rcfile=ci-coverage.ini --fail-under $minimum_required_coverage
coverage_ret_val=$?

#echo "Linting..."
flake8
echo "Testing Complete"

if [ "$unittest_ret_val" -ne "0" ] || [ "$intermediate_ret_val" -ne "0" ] || [ "$coverage_ret_val" -ne "0" ]; then

    if [ "$intermediate_ret_val" -ne "0" ]; then
        echo "Tests Failed!!!"
    fi

    if [ "$coverage_ret_val" -ne "0" ]; then
        echo "Below Minimum Coverage of $minimum_required_coverage!!!"
    fi

    return 1
fi

return 0