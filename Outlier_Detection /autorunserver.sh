#!/bin/bash

source django_website/bin/activate
cd Outlier_Detection
python3 manage.py  runserver 127.0.0.0.8000 &

exit 0
