#!/bin/bash

set -eoa pipefail

#######################################################################################
# RUN TESTS
#######################################################################################

echo Starting tests.
echo
pip3 install -r tests/requirements-tests.txt

echo
echo Waiting for deployment to become ready.
python3 tests/wait_deployment_ready.py --timeout 60

echo
echo All resources up!
echo Starting unittests...
pytest tests/ --log-cli-level="$LOG_LEVEL_TESTS"

exit 0