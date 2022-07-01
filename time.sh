#!/bin/bash
cd ~/core3-tbw/
. .venv/bin/activate
cd core
python3 tbw.py --manualPay
python3 pay.py
deactivate
