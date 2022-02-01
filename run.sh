#!/bin/bash
set -e

virtualenv -p python3 .
source ./bin/activate

pip install -e .

python -m test_lonpos_solver
