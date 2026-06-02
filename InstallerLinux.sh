#!/bin/bash

echo "Updating packages..."
sudo apt update

echo "Installing Python..."
sudo apt install -y python3 python3-pip

echo "Installing Git..."
sudo apt install -y git

echo "Cloning repo..."
git clone https://github.com/Nilsix/Bleach-Rebirth-of-Souls-Community-Patch.git