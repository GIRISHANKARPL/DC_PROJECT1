#!/usr/bin/env bash
set -o errexit

# Install system dependencies
apt-get update
apt-get install -y libportaudio2 libportaudio-dev portaudio19-dev

# Upgrade pip and install Python packages
pip install --upgrade pip
pip install -r requirements.txt
