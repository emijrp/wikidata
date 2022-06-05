#!/bin/bash

python3 -m venv pwbvenv
source pwbvenv/bin/activate
pip3 install --upgrade pip "setuptools>=49.4.0, !=50.0.0, <50.2.0" wheel
pip3 install pywikibot
pip3 install mwparserfromhell

sleep 7200

#toolforge-jobs run pwbvenv --command "./pwbvenv.sh" --image tf-python39 --wait
#toolforge-jobs run simbad-test1 --command "pwbvenv/bin/python simbad.py" --image tf-python39
#toolforge-jobs run taxon-test1 --command "pwbvenv/bin/python taxon.py" --image tf-python39
