#!/usr/bin/env bash


echo -e "Is this deployment for which type of version bump?\n\n[1] patch\n[2] minor\n[3] major"

read choice

case $choice in
    1) poetry version patch;; 
    2) poetry version minor;; 
    3) poetry version major;;
    *) echo "Invalid option";; 
esac < /dev/tty

git add pyproject.toml

git commit -m "Bump version: $(poetry version -s)"