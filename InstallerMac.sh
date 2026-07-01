#!/bin/bash

echo "Installing Python 3.11, Git and pygame..."

brew install python@3.11 git

python3.11 -m pip install --upgrade pip
python3.11 -m pip install pygame

git clone https://github.com/Nilsix/Bleach-Rebirth-of-Souls-Community-Patch.git

echo "Done."