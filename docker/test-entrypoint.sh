#!/bin/sh

#Activate virtual environment
. /app/.venv/bin/activate

#Run tests
make test

#Exit with the status of the tests
exit $?