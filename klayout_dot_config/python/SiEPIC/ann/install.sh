#! /bin/bash

# If we decide to use graphviz to create schematics...
echo "SiEPIC ANN requires graphviz and tkinter packages."
sudo apt-get install graphviz libgraphviz-dev pkg-config
sudo apt-get install python3-tk python3-pil python3-pil.imagetk
python3 -m pip install --user -r requirements.txt
