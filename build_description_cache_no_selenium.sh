#!/bin/bash

set -ex

TIMEOUT_SEC=4
    
exec python3 build_cats.py -c -w $TIMEOUT_SEC $*


