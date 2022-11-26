#!/bin/bash

python3 urls.py
head -20 urls.txt | python3 data.py