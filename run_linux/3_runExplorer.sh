#!/bin/bash

cd ..
source env/bin/activate
echo env started
export FLASK_APP=exploreData.py
export FLASK_DEBUG=0
flask run --host=0.0.0.0 -p 2000
