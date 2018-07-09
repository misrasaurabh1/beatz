#!/bin/bash
apt update -y
apt install -yq libav-tools python3-pip
pip3 install numpy scipy librosa sklearn bokeh biopython Flask