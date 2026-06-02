#!/bin/bash

echo "Installing dependencies..."


if ! command -v python3 &> /dev/null; then
    echo "Python not found, installing via Homebrew..."
    brew install python
fi

if ! command -v git &> /dev/null; then
    echo "Installing Git..."
    brew install git
fi

git clone https://github.com/Nilsix/Bleach-Rebirth-of-Souls-Community-Patch.git