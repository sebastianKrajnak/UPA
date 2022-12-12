#!/bin/bash

source venv/bin/activate
python3 urls.py
head -20 urlsDemo20.txt | python3 data.py
